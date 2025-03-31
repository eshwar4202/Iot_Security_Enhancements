#!/bin/bash

# Interface and IPs
INTERFACE="wlp0s20f3"
ESP32_IP="192.168.131.245"
SERVER_IP="192.168.131.142"
PORT="5683"

# Remove DROP rules
echo "Unblocking CoAP traffic on port $PORT..."
sudo iptables -D FORWARD -p udp --dport $PORT -j DROP 2>/dev/null
sudo iptables -D FORWARD -p udp --sport $PORT -j DROP 2>/dev/null

# Ensure forwarding rules are in place
sudo iptables -A FORWARD -p udp -s $ESP32_IP -d $SERVER_IP --dport $PORT -j ACCEPT
sudo iptables -A FORWARD -p udp -s $SERVER_IP -d $ESP32_IP --sport $PORT -j ACCEPT

echo "Traffic unblocked. Check server logs to confirm."
