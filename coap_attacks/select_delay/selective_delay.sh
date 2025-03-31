## 105 = 77 + UDP header 8 + IP header 20 = 105 bytes
## marking packets using iptables
sudo iptables -t mangle -A PREROUTING -p udp --dport 5683 -m length --length 105 -j MARK --set-mark 1

## Delay Marked Packets Using tc
sudo tc qdisc add dev wlp0s20f3 root handle 1: prio
sudo tc qdisc add dev wlp0s20f3 parent 1:3 netem delay 500ms
sudo tc filter add dev wlp0s20f3 protocol ip parent 1:0 prio 1 handle 1 fw flowid 1:3

##removal
sudo tc qdisc del dev wlp0s20f3 root
sudo iptables -t mangle -D PREROUTING -p udp --dport 5683 -m length --length 105 -j MARK --set-mark 1
