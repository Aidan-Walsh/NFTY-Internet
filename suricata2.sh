sudo sysctl -w net.ipv4.conf.all.rp_filter=0
sudo sysctl -w net.ipv4.conf.default.rp_filter=0
sudo sysctl -w net.ipv4.conf.lo.rp_filter=0
sudo sysctl -w net.ipv4.conf.enp6s0f0.rp_filter=0
sudo apt update
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -I FORWARD -i enp6s0f0 -o enp6s0f1 -j NFQUEUE
