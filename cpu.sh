cd toggle_ht
sudo bash toggle_ht.sh 0
cd ../const_freq
sudo bash const_freq.sh
cd ..
sudo ethtool -C enp1s0f0 rx-usecs 0
sudo ethtool -C enp1s0f0 tx-usecs 0
sudo ethtool -C enp6s0f0 tx-usecs 0
sudo ethtool -C enp6s0f0 rx-usecs 0
sudo ethtool -G enp1s0f0 tx 4096
sudo ethtool -G enp1s0f0 rx 4096
sudo ethtool -G enp6s0f0 tx 4096
sudo ethtool -G enp6s0f0 rx 4096

