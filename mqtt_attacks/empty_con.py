import socket

BROKER = "192.168.131.228"
PORT = 1883

while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((BROKER, PORT))
        s.close()  # Immediately close connection
    except Exception as e:
        print(f"Error: {e}")
        break
