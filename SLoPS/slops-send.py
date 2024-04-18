# from os import kill
import numpy as np
from scapy.all import *
import subprocess
import time
from scipy import stats
from decimal import *
from datetime import datetime

# import wisc_const
import sys
import paramiko
import time

R_min = 0
R_max = 500000
SEND_RATE = 0

STREAM_LENGTH = int(sys.argv[1])
PACKET_LENGTH = 30
BUDGET = 300000000
USERNAME = "Aidan_W"
USERNAME2 = "root"
SERVER_IP = "149.28.77.197"
CLIENT_IP = "128.105.145.119"
CLIENT_IP2 = "128.105.145.120"
KEY = "id_ed25519"
CLIENT_MAC = "90:e2:ba:b3:21:08"
MF_RCV_MAC = "90:e2:ba:ac:17:d0"
MF_IP = "128.105.145.106"
CLIENT_IFACE = "enp6s0f0"
SERVER_IFACE = "enp1s0f0"
SERVER_PASSWORD = "u.6Rbh$[$+vc%2AR"
CLIENT_PASSWORD = "8d4026552401\n"
SERVER = None
CLIENT = None
CLIENT_SHELL = None
SERVER_SHELL = None
NF_SHELL = None
SNORT_PATH = "/proj/netsyn-PG0/Aidan_W/snort_src/snort-2.9.20"

CTRL_C = "\x03"
CLIENT_DUMP_SHELL = None
if STREAM_LENGTH == 100: 
    F = open("slops_results_SUR_RL_MT_100.txt", "a")
else:
     F = open("slops_results_SUR_RL_MT_5000.txt", "a")
    


def client_read_check(rate):
    global SEND_RATE
    CLIENT_SHELL.send(
        "python3.9 client_read_check.py " + str(rate) + " " + str(STREAM_LENGTH) + "\n"
    )
    print("start quick sleep")
    if STREAM_LENGTH == 100:
        time.sleep(5)
    else:
        time.sleep(60)
        
    resp = CLIENT_SHELL.recv(9999)
    output = resp.decode("ascii")
    print("output of client_read_check: ")

    output = output.split()
    print(output)
    return int(output[len(output) - 2])

    # will return trend


def ssh_server():
    global SERVER_SHELL
    global SERVER
    server_ip = SERVER_IP
    password = SERVER_PASSWORD
    username = "root"

    SERVER = paramiko.client.SSHClient()

    SERVER.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SERVER.connect(server_ip, username=username, password=password)

    SERVER_SHELL = SERVER.invoke_shell()

    # client.close()


def server_command(command):

    SERVER_SHELL.send(command + "\n")
    time.sleep(1)
    resp = SERVER_SHELL.recv(9999)
    output = resp.decode("ascii")


def server_close():
    SERVER.close()


def client_scapy_stream(number, size, rate):
    global SEND_RATE
    CLIENT_SHELL.send(
        "python3.9 scapy_stream.py "
        + str(number)
        + " "
        + str(size)
        + " "
        + str(rate)
        + " "
        + str(SEND_RATE)
        + "\n"
    )
    if STREAM_LENGTH == 100:
        time.sleep(3)
    else:
        time.sleep(10)
    resp = CLIENT_SHELL.recv(9999)
    output = resp.decode("ascii")
    print("output of client_scapy_stream: ")
    output = output.split()
    print(output)
    SEND_RATE = float(output[len(output) - 2])


def client_command(command):
    CLIENT_SHELL.send(command + "\n")
    time.sleep(1)
    resp = CLIENT_SHELL.recv(9999)
    output = resp.decode("ascii")
    print(output)


def client_dump_command(command):
    CLIENT_DUMP_SHELL.send(command + "\n")
    time.sleep(1)
    resp = CLIENT_DUMP_SHELL.recv(9999)
    output = resp.decode("ascii")
    print(output)


def client_close():
    #client_command("route delete default gw 192.168.0.2 enp6s0f0")
    CLIENT.close()


def ssh_client():
    global CLIENT_SHELL
    global CLIENT
    global CLIENT_DUMP_SHELL
    client_ip = CLIENT_IP
    password = CLIENT_PASSWORD
    username = "Aidan_W"
    CLIENT = paramiko.client.SSHClient()

    CLIENT.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    CLIENT.connect(client_ip, username=username)
    CLIENT_SHELL = CLIENT.invoke_shell()

    CLIENT_SHELL.send("cd /proj/netsyn-PG0/Aidan_W/NFTY/\n")
    time.sleep(1)
    resp = CLIENT_SHELL.recv(9999)
    output = resp.decode("ascii")

    CLIENT_SHELL.send("su\n")
    time.sleep(1)
    resp = CLIENT_SHELL.recv(9999)
    output = resp.decode("ascii")

    # now in correct directory as root
    CLIENT_SHELL.send(password)
    time.sleep(1)
    resp = CLIENT_SHELL.recv(9999)
    output = resp.decode("ascii")

    CLIENT_DUMP_SHELL = CLIENT.invoke_shell()

    CLIENT_DUMP_SHELL.send("cd /proj/netsyn-PG0/Aidan_W/NFTY/\n")
    time.sleep(1)
    resp = CLIENT_DUMP_SHELL.recv(9999)
    output = resp.decode("ascii")

    CLIENT_DUMP_SHELL.send("su\n")
    time.sleep(1)
    resp = CLIENT_DUMP_SHELL.recv(9999)
    output = resp.decode("ascii")

    # now in correct directory as root
    CLIENT_DUMP_SHELL.send(password)
    time.sleep(1)
    resp = CLIENT_DUMP_SHELL.recv(9999)
    output = resp.decode("ascii")

    #client_command("route add default gw 192.168.0.2 enp6s0f0")


def scapy_stream(number, size, rate):
    global SEND_RATE
    packets_list = []
    for i in range(number):
        src_ip = CLIENT_IP  # + str(random.randint(0, 200))
        # src_ip = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
        data = "X" * size
        pkt = Ether(src=CLIENT_MAC, dst=MF_RCV_MAC) / IP(
            dst=SERVER_IP, src=src_ip, id=i
        )
        pkt = pkt / UDP(dport=12345, sport=6666) / Raw(load=data)
        # pkt = pkt/TCP(dport=12345,flags="S",seq=1)/Raw(load=data)
        packets_list.append(pkt)
    # send(pkt)
    loop_times = 1  # (rate / 1000)
    # print(f"Now sending at rate {rate}pps")
    output = sendpfast(
        packets_list, pps=rate, loop=1, parse_results=1, iface=CLIENT_IFACE
    )
    print(output)
    SEND_RATE = output["pps"]
    # print(output)


def calculate_rate(R_max, R_min):
    rate = (R_max + R_min) / 2
    return rate


def start_capture(rate):
    username = USERNAME
    ip = SERVER_IP
    key = KEY
    username2 = USERNAME2

    server_command(
        "tcpdump -i "
        + SERVER_IFACE
        + " -w /root/slops/slops"
        + str(rate)
        + "_rcv.pcap src "
        + CLIENT_IP + " or " + CLIENT_IP2
    )
    print("create server capture")
    client_dump_command(
        "tcpdump -i "
        + CLIENT_IFACE
        + " -w /proj/netsyn-PG0/Aidan_W/slops/slops"
        + str(rate)
        + "_snd.pcap dst "
        + SERVER_IP
    )
    """ subprocess.Popen(
        [
            "sudo",
            "tcpdump",
            "-i",
            CLIENT_IFACE,
            "-w",
            "/proj/netsyn-PG0/Aidan_W/slops/slops{rate}_snd.pcap",
            "port",
            "12345",
        ]
    ) """


def fetch_file(rate):
    username = USERNAME
    username2 = USERNAME2
    ip = SERVER_IP
    key = KEY
    server_command(CTRL_C)
    # output = subprocess.check_output(["ssh", "-i", f"/users/{username}/.ssh/{key}",f"{username2}@{ip}","sudo","killall","tcpdump"])
    # subprocess.check_output(["sudo", "killall", "tcpdump"])
    client_dump_command(CTRL_C)
    time.sleep(2)
    print("sending to scp:")
    #client_command("route delete default gw 192.168.0.2 enp6s0f0")
    client_command(
        "scp -i /users/Aidan_W/.ssh/"
        + key
        + " "
        + username2
        + "@"
        + ip
        + ":/root/slops/slops"
        + str(rate)
        + "_rcv.pcap /proj/netsyn-PG0/Aidan_W/slops/"
    )
    #client_command("yes")
    time.sleep(10)
    client_command(SERVER_PASSWORD)
    #client_command("route add default gw 192.168.0.2 enp6s0f0")
    print("copied over files")

    """cur_stats = subprocess.check_output(
        [
            "scp",
            "-i",
            f"/users/{username}/.ssh/{key}",
            f"{username2}@{ip}:/root/slops/slops{rate}_rcv.pcap",
            f"/users/{username}/slops/",
        ]
    ) """


def get_pkt_by_id(packets, id):
    for p in packets:
        if p.id == id:
            return p
    return None


def read_owds(rate):
    global STREAM_LENGTH
    path = "/proj/netsyn-PG0/Aidan_W/slops"
    pcap_snd = rdpcap(f"{path}/slops{rate}_snd.pcap")
    pcap_rcv = rdpcap(f"{path}/slops{rate}_rcv.pcap")
    owds = [0] * STREAM_LENGTH
    total_packets = 0
    # print(len(pcap_snd),len(pcap_rcv))
    for i in range(STREAM_LENGTH):
        id = pcap_snd[i].id
        rcv_pkt = get_pkt_by_id(pcap_rcv, id)
        owd = float(rcv_pkt.time - pcap_snd[i].time) * 1000000
        owds[i] = owd

    return owds


def check_pct(grp_median, group_num):
    output = 0
    for j in range(1, group_num):
        # print(j, j-1, grp_median)
        if grp_median[j] > grp_median[j - 1]:
            output += 1
    pct = output / (group_num - 1)
    # print(pct,"pct")
    return pct


def check_pdt(grp_median, group_num):
    output = 0
    for j in range(1, group_num):
        output += np.absolute(grp_median[j] - grp_median[j - 1])
    pdt = (grp_median[-1] - grp_median[0]) / output
    # print(pdt,"pdt")
    return pdt


def check_trend(owds):
    global STREAM_LENGTH
    length = STREAM_LENGTH  # - 10
    group_num = int(math.sqrt(length))
    owds = owds[10:]
    groups = np.array_split(owds, group_num)
    median_array = np.array([np.median(grp) for grp in groups])
    # print(np.shape(median_array), group_num)
    pct_test = check_pct(median_array, group_num)

    if pct_test <= 0.55:
        pdt_test = check_pdt(median_array, group_num)
        if pdt_test > 0.4:
            return 1
        else:
            return 0
    else:
        return 1


def readjust_rate(trend, rate):
    global R_min, R_max, SEND_RATE
    if trend == 1:
        R_max = SEND_RATE
    else:
        R_min = SEND_RATE
    print("balls")
    print(SEND_RATE)
    print(R_max)
    print(R_min)


def send_streams():
    global F
    global R_max, R_min, STREAM_LENGTH, PACKET_LENGTH, BUDGET
    rate = 0
    used_budget = 0
    while R_max - R_min > 1000 and BUDGET > 0:
        rate = calculate_rate(R_max, R_min)
        # print(f"Now sending at rate {rate}pps")
        start_capture(rate)
        time.sleep(2)

        # scapy_stream(STREAM_LENGTH, PACKET_LENGTH, rate)
        client_scapy_stream(STREAM_LENGTH, PACKET_LENGTH, rate)
        time.sleep(3)
        fetch_file(rate)
        trend = client_read_check(rate)
        """owds = read_owds(rate)
        # print(owds)
        trend = check_trend(owds) """

        if trend == 1:
            print("increasing trend")
        print(rate)
        readjust_rate(trend, rate)
        # print(f"readjusted {R_min},{R_max}")
        BUDGET = BUDGET - STREAM_LENGTH
        # print(f"remaining budget is {BUDGET}")
        used_budget += STREAM_LENGTH
    print(f"NF detected rate = {SEND_RATE}")
    F.write(f"NF detected rate = {SEND_RATE} ; budget_used = {used_budget}\n")
    F.close()


if __name__ == "__main__":
    ip = MF_IP
    ssh_client()
    ssh_server()
    #subprocess.Popen(["ssh", f"Aidan_W@{ip}","sudo","t\
#askset", "3",f"{SNORT_PATH}/bin/snort", "-Q", "-A","none", "-c", f"{SNORT_PATH}/nfq.conf", "--da\
#q-var", "queue_len=65535"])
    #time.sleep(1)
    send_streams()
    client_close()
    server_close()
    #subprocess.check_output(["ssh",f"Aidan_W@{ip}", "sudo","killall",f"{SNORT_PATH}/bin/snort"])
    #time.sleep(1)
