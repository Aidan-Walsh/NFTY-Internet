sudo iptables -D FORWARD 1
sudo iptables -I FORWARD -i $MF_RCV_IFACE -o $MF_FWD_IFACE -j NFQUEUE