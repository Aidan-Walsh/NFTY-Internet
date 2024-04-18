
from statistics import mean
from scapy.all import *
from scipy import stats

import sys
import numpy as np



def get_dispersion(r_probe):
    last_pkt = r_probe[0]
    r_dispersion = np.array([])
    f = open("dispersions.txt","w")
    start = 0
    string = ""
    mean_disps = []
    median_disps = []
    f.write("[")
    for i in range(1,len(r_probe)):  
        if("IP" in r_probe[i]):
            if(last_pkt):
                dispersion = float(r_probe[i].time - last_pkt.time)
                last_pkt=r_probe[i]
                print(dispersion,i)
                
                r_dispersion = np.append(r_dispersion,dispersion)
                f.write(str(dispersion))
                f.write(",")
           
    print("stats",np.mean(r_dispersion), np.median(r_dispersion),np.std(r_dispersion))
                # 
    f.write("]")
    f.close()



def main(filename):
    pcap = rdpcap(filename)
    get_dispersion(pcap)
    


if __name__=="__main__":
    rcv_filename = sys.argv[1]
    
    main(rcv_filename)