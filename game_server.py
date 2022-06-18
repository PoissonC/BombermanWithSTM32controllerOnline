import socket
from threading import Thread
import pickle
import json
server = "10.140.0.2" #Our server local ip
port = 5555
class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args , **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

def get_client(conn,data):
    m=json.loads(conn.recv(2048*128))
    return m


data=dict()
conn1, addr1 = s.accept()
print("Connected to:", addr1)
conn2, addr2 = s.accept()
print("Connected to:", addr2)
conn3, addr3 = s.accept()
print("Connected to:", addr3)
conn4, addr4 = s.accept()
print("Connected to:", addr4)
while True:
        T1=ThreadWithReturnValue(target=get_client,args=(conn1,data))
        T2=ThreadWithReturnValue(target=get_client,args=(conn2,data))
        T1.start()
        T2.start()
        a=T1.join()
        b=T2.join()
        data['x1']=a['x']
        data['y1']=a['y']
        data['z1']=a['z']
        data['x2']=b['x']
        data['y2']=b['y']
        data['z2']=b['z']
        try:
            conn3.sendall(pickle.dumps(data))
            conn4.sendall(pickle.dumps(data))
        except:
            print('sending data error')
            
