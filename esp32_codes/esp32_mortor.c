#include <ESP32Servo.h>
Servo servo;
#include <WiFi.h>
#include <PubSubClient.h>

const char *ssid = "Eshwar";
const char *password = "pavethran42";
const char *mqtt_broker = "192.168.157.228";
const char *mqtt_topic_pub = "esp32/capture";    // Topic to publish to
const char *mqtt_topic_sub = "esp32/vehicle_count"; // Topic to subscribe to
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

// Global variables
int count1 = 1;
int count2 = 1;
unsigned long lastActionTime = 0;
const unsigned long actionDelay = 2000;     // Delay between regular actions
unsigned long lastDualIRTime = 0;           // Timestamp of last dual-IR event
const unsigned long dualIRCooldown = 30000; // 30-second cooldown for dual-IR case
unsigned long lastReconnectAttempt = 0;     // Timestamp of last MQTT reconnect attempt
const unsigned long reconnectInterval = 5000; // 5-second interval between reconnect attempts
String message;

// Non-blocking timing for dual-IR sequence
enum DualIRState { IDLE, LANE2_START, LANE2_WAIT, LANE1_START, LANE1_WAIT };
DualIRState dualIRState = IDLE;
unsigned long dualIRStepTime = 0;
const unsigned long dualIRStepDelay = 1000; // 1-second delay between steps

// Vehicle counts for each lane
int lane1Count = 0;
int lane2Count = 0;

// GPIO pins for lane comparison
const int lane1Pin = 18;  // GPIO 5 for lane 1
const int lane2Pin = 19;  // GPIO 6 for lane 2
const int lane1Pin2 = 4;

void setup() {
  Serial.begin(115200);
  servo.attach(15);
  pinMode(16, INPUT);
  pinMode(17, INPUT);
  pinMode(lane1Pin, OUTPUT); // Set GPIO 5 as output
  pinMode(lane2Pin, OUTPUT); // Set GPIO 6 as output
  pinMode(lane1Pin2,OUTPUT);
  digitalWrite(lane1Pin, LOW);
  digitalWrite(lane1Pin2, LOW); // Initially low
  digitalWrite(lane2Pin, LOW); // Initially low

  WiFi.begin(ssid, password);
  WiFi.setSleep(false);
  Serial.print("WiFi connecting...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi Connected!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());
  Serial.print("WiFi Signal Strength (RSSI): ");
  Serial.println(WiFi.RSSI());

  testBrokerConnectivity();
  client.setServer(mqtt_broker, mqtt_port);
  client.setKeepAlive(60); // Set keep-alive to 60 seconds
  client.setCallback(mqttCallback); // Set callback for incoming messages
  reconnectMQTT();
}

void testBrokerConnectivity() {
  WiFiClient testClient;
  Serial.print("Testing connection to broker ");
  Serial.print(mqtt_broker);
  Serial.print(":");
  Serial.print(mqtt_port);
  Serial.print("...");
  if (testClient.connect(mqtt_broker, mqtt_port)) {
    Serial.println("✅ Broker reachable!");
    testClient.stop();
  } else {
    Serial.println("❌ Failed to reach broker!");
  }
}

void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("🔌 Connecting to MQTT at ");
    Serial.print(mqtt_broker);
    Serial.print(":");
    Serial.print(mqtt_port);
    Serial.print("...");
    String clientId = "ESP32-" + String(WiFi.macAddress());
    unsigned long start = millis();
    if (client.connect(clientId.c_str())) {
      Serial.print("✅ Connected in ");
      Serial.print(millis() - start);
      Serial.println(" ms!");
      client.subscribe(mqtt_topic_sub); // Subscribe to vehicle count topic
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" - Retrying in 5s...");
      delay(5000);
    }
  }
}

void mqttCallback(char *topic, byte *payload, unsigned int length) {
  // Convert payload to string
  String msg = "";
  for (unsigned int i = 0; i < length; i++) {
    msg += (char)payload[i];
  }
  Serial.print("📩 Received message on ");
  Serial.print(topic);
  Serial.print(": ");
  Serial.println(msg);

  // Parse message in format "lane number: vehicle count"
  int colonIndex = msg.indexOf(':');
  if (colonIndex != -1) {
    String lane = msg.substring(0, colonIndex);
    lane.trim(); // Remove leading/trailing spaces
    String countStr = msg.substring(colonIndex + 1);
    countStr.trim();
    int vehicleCount = countStr.toInt();

    // Update lane counts
    if (lane == "lane 1") {
      lane1Count = vehicleCount;
    } else if (lane == "lane 2") {
      lane2Count = vehicleCount;
    }

    // Compare and set GPIO pins
    if (lane1Count > lane2Count) {
      digitalWrite(lane1Pin, HIGH);
      digitalWrite(lane1Pin2, HIGH);
      digitalWrite(lane2Pin, LOW);
      Serial.println("Lane 1 has more vehicles - GPIO 5 HIGH, GPIO 6 LOW");
    } else if(lane2Count > lane1Count) {
      digitalWrite(lane1Pin, LOW);
      digitalWrite(lane2Pin, HIGH);
      digitalWrite(lane1Pin2, LOW);
      Serial.println("Lane 2 has more or equal vehicles - GPIO 5 LOW, GPIO 6 HIGH");
    }
    else{
      digitalWrite(lane1Pin,LOW);
      digitalWrite(lane1Pin2, LOW);
      digitalWrite(lane2Pin,LOW);
    }
  } else {
    
    Serial.println("❌ Invalid message format");
  }
}

void loop() {
  if (!client.connected()) {
    unsigned long currentTime = millis();
    if (currentTime - lastReconnectAttempt >= reconnectInterval) {
      Serial.println("MQTT disconnected, attempting reconnect...");
      testBrokerConnectivity();
      reconnectMQTT();
      lastReconnectAttempt = currentTime;
    }
  }
  client.loop();

  int ir1 = digitalRead(16);
  int ir2 = digitalRead(17);
  unsigned long currentTime = millis();

  // Condition 1: ir1 detects, ir2 does not
  if (ir1 == 0 && ir2 == 1 && currentTime - lastActionTime >= actionDelay) {
    servo.write(100);
    if (count1 == 1) {
      count1 = 0;
      message = "lane 1";
      if (client.publish(mqtt_topic_pub, message.c_str())) {
        Serial.println("Servo to 100° - Sent message to cam (ir1)");
      } else {
        Serial.println("Servo to 100° - Failed to send message");
      }
      count2 = 1;
    }
    lastActionTime = currentTime;
  }

  // Condition 2: ir2 detects, ir1 does not
  if (ir2 == 0 && ir1 == 1 && currentTime - lastActionTime >= actionDelay) {
    servo.write(260);
    if (count2 == 1) {
      message = "lane 2";
      count2 = 0;
      if (client.publish(mqtt_topic_pub, message.c_str())) {
        Serial.println("Servo to 260° - Sent message to cam (ir2)");
      } else {
        Serial.println("Servo to 260° - Failed to send message");
      }
      count1 = 1;
    }
    lastActionTime = currentTime;
  }

  // Condition 3: Both IRs detect (with 30-second cooldown, non-blocking)
  if (ir1 == 0 && ir2 == 0 && currentTime - lastDualIRTime >= dualIRCooldown) {
    switch (dualIRState) {
      case IDLE:
        servo.write(260);
        dualIRStepTime = currentTime;
        dualIRState = LANE2_START;
        break;

      case LANE2_START:
        if (currentTime - dualIRStepTime >= dualIRStepDelay) {
          message = "lane 2";
          if (client.publish(mqtt_topic_pub, message.c_str())) {
            Serial.println("Servo to 260° - Sent message to cam (dual IR, lane 2)");
          } else {
            Serial.println("Servo to 260° - Failed to send message (dual IR, lane 2)");
          }
          dualIRStepTime = currentTime;
          dualIRState = LANE2_WAIT;
        }
        break;

      case LANE2_WAIT:
        if (currentTime - dualIRStepTime >= dualIRStepDelay) {
          servo.write(100);
          dualIRStepTime = currentTime;
          dualIRState = LANE1_START;
        }
        break;

      case LANE1_START:
        if (currentTime - dualIRStepTime >= dualIRStepDelay) {
          message = "lane 1";
          if (client.publish(mqtt_topic_pub, message.c_str())) {
            Serial.println("Servo to 100° - Sent message to cam (dual IR, lane 1)");
          } else {
            Serial.println("Servo to 100° - Failed to send message (dual IR, lane 1)");
          }
          dualIRStepTime = currentTime;
          dualIRState = LANE1_WAIT;
        }
        break;

      case LANE1_WAIT:
        if (currentTime - dualIRStepTime >= dualIRStepDelay) {
          lastDualIRTime = currentTime; // Update cooldown timestamp
          lastActionTime = currentTime; // Update regular action time
          dualIRState = IDLE;           // Reset state
        }
        break;
    }
  } else if (ir1 == 0 && ir2 == 0 && currentTime - lastDualIRTime < dualIRCooldown) {
    Serial.println("Dual IR detected, but in cooldown period - skipping...");
    dualIRState = IDLE; // Reset state if in cooldown
  } else {
    dualIRState = IDLE; // Reset state if not in dual-IR condition
  }
}
