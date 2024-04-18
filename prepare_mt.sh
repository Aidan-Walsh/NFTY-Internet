sudo iptables -D FORWARD 1
sudo sudo iptables -I FORWARD -i $MF_RCV_IFACE -o $MF_FWD_IFACE -j NFQUEUE --queue-balance 0:1