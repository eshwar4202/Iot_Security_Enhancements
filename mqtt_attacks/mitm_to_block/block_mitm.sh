#!/bin/bash

# Interface and IPs
INTERFACE="wlp0s20f3"
ESP32_IP="192.168.115.245"
SERVER_IP="192.168.115.228"
PORT="1883"

# Insert DROP rule at the top
echo "Blocking MQTT traffic on port $PORT..."
sudo iptables -A FORWARD -p tcp --dport 1883 -j DROP ~ 4
sudo iptables -A FORWARD -p tcp --sport 1883 -j DROP

echo "Traffic blocked. Check server logs to confirm."
