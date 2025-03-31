#include "esp_camera.h"
#include <WiFi.h>
#include <PubSubClient.h>
#include <HTTPClient.h>

#define CAMERA_MODEL_AI_THINKER  // Has PSRAM
#include "camera_pins.h"

// 🔒 WiFi Credentials
const char *ssid = "Eshwar";
const char *password = "pavethran42";

// 🌐 MQTT + Flask Server
const char *mqtt_broker = "192.168.157.228"; // MQTT Broker
const char *mqtt_topic = "esp32/capture";    // MQTT Topic
const char *flask_server = "http://192.168.157.179:5000/upload";  // Flask Server

WiFiClient espClient;
PubSubClient client(espClient);

// Define the flash pin (GPIO 4 on AI-Thinker ESP32-CAM)
#define FLASH_PIN 4

// 📸 Capture & Send Image with Lane Number
void capture_and_send(const char *lane_number) {
  Serial.println("📸 Capturing image...");

  // Turn on the flash
  digitalWrite(FLASH_PIN, HIGH);
  Serial.println("💡 Flash ON");
  delay(200); // Wait a bit so flash is fully on

  // Capture image
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("❌ Camera capture failed!");
    digitalWrite(FLASH_PIN, LOW);
    Serial.println("💡 Flash OFF");
    return;
  }

  // Turn off the flash
  digitalWrite(FLASH_PIN, LOW);
  Serial.println("💡 Flash OFF");
  Serial.printf("✅ Image captured successfully, size: %u bytes\n", fb->len);
  Serial.printf("📡 Sending image and lane number '%s' to Flask server...\n", lane_number);

  HTTPClient http;
  http.setTimeout(10000); // 10-second timeout
  Serial.println("🔗 Attempting to connect to Flask server...");
  if (!http.begin(flask_server)) {
    Serial.println("❌ Failed to initialize HTTP connection!");
    esp_camera_fb_return(fb);
    return;
  }

  // Define boundary without extra dashes so that header and body format correctly
  String boundary = "ESP32BOUNDARY";
  String contentType = "multipart/form-data; boundary=" + boundary;

  // Create multipart body parts
  String bodyStart = "--" + boundary + "\r\n";
  bodyStart += "Content-Disposition: form-data; name=\"lane\"\r\n\r\n";
  bodyStart += String(lane_number) + "\r\n";
  bodyStart += "--" + boundary + "\r\n";
  bodyStart += "Content-Disposition: form-data; name=\"image\"; filename=\"capture.jpg\"\r\n";
  bodyStart += "Content-Type: image/jpeg\r\n\r\n";

  String bodyEnd = "\r\n--" + boundary + "--\r\n";

  size_t fullLength = bodyStart.length() + fb->len + bodyEnd.length();
  Serial.printf("📏 Full request size: %u bytes\n", fullLength);

  // Allocate memory for the full request body
  uint8_t *fullBody = (uint8_t *)malloc(fullLength);
  if (!fullBody) {
    Serial.printf("❌ Failed to allocate %u bytes for full body!\n", fullLength);
    esp_camera_fb_return(fb);
    http.end();
    return;
  }

  // Construct full body: header, image data, and closing boundary
  memcpy(fullBody, bodyStart.c_str(), bodyStart.length());
  memcpy(fullBody + bodyStart.length(), fb->buf, fb->len);
  memcpy(fullBody + bodyStart.length() + fb->len, bodyEnd.c_str(), bodyEnd.length());

  // Set headers
  http.addHeader("Content-Type", contentType);
  http.addHeader("Content-Length", String(fullLength));

  // Send the full request
  Serial.println("📨 Sending HTTP POST request...");
  int httpResponseCode = http.POST(fullBody, fullLength);

  if (httpResponseCode > 0) {
    Serial.printf("✅ Image sent! Server responded: %d\n", httpResponseCode);
    String response = http.getString();
    Serial.println("Server response body: " + response);
  } else {
    Serial.printf("❌ HTTP request failed with error: %s\n", http.errorToString(httpResponseCode).c_str());
  }

  // Clean up
  free(fullBody);
  esp_camera_fb_return(fb);
  http.end();
}

// 📡 MQTT Callback (Handles Incoming Messages)
void mqtt_callback(char *topic, byte *payload, unsigned int length) {
  Serial.println("📩 MQTT Trigger Received!");

  char message[length + 1];
  memcpy(message, payload, length);
  message[length] = '\0'; // Null-terminate the string

  Serial.printf("🚦 Triggering capture for lane: %s\n", message);
  capture_and_send(message);
}

// 📶 WiFi + MQTT Setup
void setup() {
  Serial.begin(115200);
  Serial.println();

  // Configure the flash pin as output and turn it off initially
  pinMode(FLASH_PIN, OUTPUT);
  digitalWrite(FLASH_PIN, LOW);
  Serial.println("💡 Flash pin initialized");

  // 🔗 Connect to WiFi
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);
  Serial.print("WiFi connecting...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi Connected!");
  Serial.printf("IP Address: %s\n", WiFi.localIP().toString().c_str());

  // 🔗 Connect to MQTT
  client.setServer(mqtt_broker, 1883);
  client.setCallback(mqtt_callback);

  while (!client.connected()) {
    Serial.print("🔌 Connecting to MQTT...");
    if (client.connect("ESP32CAM")) {
      Serial.println("✅ Connected!");
      client.subscribe(mqtt_topic);
    } else {
      Serial.print(".");
      delay(1000);
    }
  }

  // 📷 Camera Configuration
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA; // 320x240
  config.jpeg_quality = 12; // Lower value means higher quality
  config.fb_count = 1;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_DRAM;

  // Adjust for PSRAM if available
  if (psramFound()) {
    Serial.println("✅ PSRAM detected! Using high-quality settings.");
    config.jpeg_quality = 10;
    config.fb_count = 2;
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.grab_mode = CAMERA_GRAB_LATEST;
  }

  // 📷 Initialize Camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("❌ Camera init failed: 0x%x\n", err);
    return;
  }

  // Correct image orientation if necessary
  sensor_t *s = esp_camera_sensor_get();
  if (s->id.PID == OV2640_PID || s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);
    s->set_hmirror(s, 1);
    Serial.println("✅ Image orientation corrected");
  }

  if (s->id.PID == OV3660_PID) {
    s->set_brightness(s, 1);
    s->set_saturation(s, -2);
  }
}

// 🔄 Loop (Handle MQTT)
void loop() {
  if (!client.connected()) {
    Serial.println("🔌 MQTT disconnected, reconnecting...");
    if (client.connect("ESP32CAM")) {
      client.subscribe(mqtt_topic);
    }
  }
  client.loop();
}

