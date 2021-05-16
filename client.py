# Python TCP Client A
import socket 
from threading import Thread
import time
import sys
# serverIPs = ["127.0.0.1"]
# serverIPs = ["192.168.122.156"]
serverIPs = ["192.168.122.53"]
class ListeningIP(Thread):
    def __init__(self,port): 
        Thread.__init__(self) 
        self.port = port
    def run(self):
        print(serverIPs)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        s.bind(('0.0.0.0', self.port))
        s.listen(5)
        while 1:
            (conn, (ip,port)) =  s.accept()
            data = conn.recv(1024).decode()
            serverIPs.append(data)
            print("Started Using These IPs",serverIPs)
            conn.close()
        s.close()
class RecieveData(Thread):
    def __init__(self,port): 
        Thread.__init__(self) 
        self.port = port
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        s.bind(('0.0.0.0', self.port))
        s.listen(5)
        while 1:
            (conn, (ip,port)) =  s.accept()
            data = conn.recv(1024).decode()
            print("Recieved ",data," from ",ip)
            conn.close()
        s.close() 
class SendData(Thread):
    def __init__(self,port,iters):
        Thread.__init__(self) 
        self.port = port
        self.iters = iters
    def run(self):
        n = 10000000
        j=0
        while 1:
            for i in range(4*self.iters):
                if i%self.iters==0:
                    print("Iteration Number:", i)
                if i == 0:
                    n = 1500000
                    print("Started running in Low Load Mode")
                elif i == self.iters:
                    n = 12500000
                    print("Started running in High Load Mode")
                for ip in serverIPs:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        s.connect((ip, self.port))
                    except:
                        print("Couldn't connect to ",ip)
                        time.sleep(1)
                        continue
                    s.send(str(n).encode())     
                    if j%2==0:
                        n=n+5
                    else:
                        n=n-5
                    j=j+1
                    time.sleep(1)

        s.close()
iterToSwitch = sys.argv[1]
t1=ListeningIP(2005)
t2=SendData(2004,int(iterToSwitch))
t3=RecieveData(2006)
t1.start()
t2.start()
t3.start()
t1.join()
t2.join()
t3.join()