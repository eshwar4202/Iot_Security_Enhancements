#!/bin/bash

# Interface and IPs
INTERFACE="wlp0s20f3"
ESP32_IP="192.168.131.245"
SERVER_IP="192.168.131.142"
PORT="5683"

# Insert DROP rule at the top
echo "Blocking CoAP traffic on port $PORT..."
sudo iptables -I FORWARD 1 -p udp --dport $PORT -j DROP
sudo iptables -I FORWARD 2 -p udp --sport $PORT -j DROP

echo "Traffic blocked. Check server logs to confirm."
