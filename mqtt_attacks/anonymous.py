import paho.mqtt.client as mqtt

BROKER = "192.168.131.228"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[+] Broker allows anonymous access!")
    else:
        print("[-] Anonymous access denied.")


client = mqtt.Client()
client.on_connect = on_connect
client.connect(BROKER, 1883, 60)
client.loop_forever()
