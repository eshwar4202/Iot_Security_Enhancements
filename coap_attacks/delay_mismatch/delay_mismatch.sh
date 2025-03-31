## delaying all the msg by 5 seconds
sudo tc qdisc add dev wlp0s20f3 root handle 1: prio
sudo tc qdisc add dev wlp0s20f3 parent 1:3 netem delay 5000ms # 5-second delay
sudo tc filter add dev wlp0s20f3 protocol ip parent 1:0 prio 1 u32 match ip src 192.168.251.142 flowid 1:3

coap-client -m get -T 0x77 coap://192.168.251.142/test # intial request to server

## send the below after 2 to 3 seconds
coap-client -m get -T 0x77 coap://192.168.251.142/test2

sudo tcpdump -i wlp0s20f3 udp port 5683
