from __future__ import print_function
import sys
import libvirt
import time
from threading import Thread
import socket
# domName = 'vm_2'
scaled = False
starting_VM = False
conn = libvirt.open('qemu:///system')
if conn == None:
    print('Failed to open connection to qemu:///system', file=sys.stderr)
    exit(1)
dom1 = conn.lookupByName('vm_1')
dom2 = conn.lookupByName('vm_2')

if dom1 == None or dom2 == None:
    print('Failed to find the domain', file=sys.stderr)
    exit(1)
def returnUsage(s1, s2):
    x=s2[0]['cpu_time'] - s2[0]['user_time'] - s2[0]['system_time']
    y=s1[0]['cpu_time'] - s1[0]['user_time'] - s1[0]['system_time']
    return 100*(x - y) / 1e9
class SendIPThread(Thread):
        def __init__(self,port): 
            Thread.__init__(self) 
            self.port = port
        def run(self):
            dom2.create()
            time.sleep(40)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            done = False
            while not(done):
                try:
                    s.connect(('127.0.0.1', self.port))
                    done=True
                except:
                    print("Trying to connect to spawned VM")
                    time.sleep(2)
            s.send("192.168.122.156".encode())
            print("SENT ip",'192.168.122.156')
            s.close()
if __name__ == "__main__":
    average1=[]
    average2=[]
    while 1:
        p=0
        # for _ in range(5):
        t1 = time.time()
        stats_1 = dom1.getCPUStats(True)
        scaled = dom2.isActive()
        if scaled:
            stats_2 = dom2.getCPUStats(True)
        time.sleep(5)
        stats_1_t = dom1.getCPUStats(True)
        if scaled:
            stats_2_t = dom2.getCPUStats(True)
        t2 = time.time()
        # stats2 = dom.getCPUStats(True)
        # req_1 = stats_1[0]['cpu_time'] - stats_1[0]['user_time'] - stats_1[0]['system_time']
        # req_1_t = stats2[0]['cpu_time'] - stats2[0]['user_time'] - stats2[0]['system_time']
        # usage = 100*(req2 -req) / ((time.time() - t1) * 1e9)
        # print(100*(stats2[0]['cpu_time'] - stats[0]['cpu_time']) / ((time.time() - t1) * 1e9))
        # p+=100*(req2 -req) / ((time.time() - t1) * 1e9)
        # print(100*(req2 -req) / ((time.time() - t1) * 1e9))
        usage1=returnUsage(stats_1,stats_1_t)/(t2-t1)
        print("vm_1 CPU usage:", usage1)
        if scaled:
            usage2=returnUsage(stats_2,stats_2_t)/(t2-t1)
            print("vm_2 CPU usage:", usage2)
            average2.append(usage2)
        average1.append(usage1)
        if len(average1) >= 5:
            average1 = average1[-5:]
            av1 = sum(average1)/5
            print("vm_1 Average of last 5 measurements (about 25 seconds):",av1)
            if scaled and len(average2)>=5:
                average2 = average2[-5:]
                av2 = sum(average2)/5
                print("vm_2 Average of last 5 measurements (about 25 seconds):",av2)
            if av1 > 80 and not(starting_VM):
                print("OVERLOAD")
                starting_VM = True
                t=SendIPThread(2005)
                t.start()
    conn.close()
    exit(0)