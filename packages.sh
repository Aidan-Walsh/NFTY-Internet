sudo apt update
sudo apt-get install build-essential libpcap-dev   \
                libnet1-dev libyaml-0-2 libyaml-dev pkg-config zlib1g zlib1g-dev \
                libcap-ng-dev libcap-ng0 make libmagic-dev         \
                libgeoip-dev liblua5.1-dev libhiredis-dev libevent-dev \
                python-yaml rustc cargo libpcre3-dev libjansson-dev

sudo apt-get install libnetfilter-queue-dev libnetfilter-queue1  \
                libnetfilter-log-dev libnetfilter-log1      \
                libnfnetlink-dev libnfnetlink0

sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev

wget https://www.python.org/ftp/python/3.9.1/Python-3.9.1.tgz

tar -xf Python-3.9.1.tgz

cd Python-3.9.1

./configure --enable-optimizations

make -j 12

sudo make altinstall

sudo pip3.9 install scipy scapy numpy

sudo apt-get install tcpreplay

sudo apt-get install hping3
