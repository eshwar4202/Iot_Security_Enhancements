#!/bin/bash

# Stop ARP spoofing
echo "Stopping ARP spoofing..."
sudo pkill arpspoof

# Flush iptables and disable forwarding
echo "Resetting iptables and disabling IP forwarding..."
sudo iptables -F
sudo iptables -t nat -F
sudo iptables -P FORWARD ACCEPT
sudo sysctl -w net.ipv4.ip_forward=0

echo "MITM stopped and network reset."
