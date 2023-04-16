import socket
import threading
import json
import sys
import requests
import argparse
import pymongo
from pymongo import MongoClient

try:
	conn = MongoClient("localhost",27017)
	print("Connected successfully!!!")
except:
	print("Could not connect to MongoDB")


db = conn.users
collection = db.servers

HOST = ""

## if central_server run with PORT =10000
PORT = 10000
HEADER = 64
DB_URL = "http://127.0.0.1:8080/server_map"

parser = argparse.ArgumentParser()
parser.add_argument("-PORT" ,"--port_no", help = "Show Output")
args = parser.parse_args()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if(args.port_no!=None):
    PORT=args.port_no

def log(statement,value=""):
    print(f"[ {statement} ]",end=" ")
    if(value!=""):
        print(f": {value}",end="")
    print()

try:
    if(args.port_no==None):
        log("Trying to Bind to default port ")
    else:
        log(f"Trying to Bind to PORT :{PORT}")
    PORT=int(PORT)
    server.bind((HOST, PORT))
except :
    log(f"Failed to connect")

else:
    log("Listening to PORT {} ...".format(PORT),"succesful")





def recv_msg(connection,port):
    length=connection.recv(HEADER).decode("utf-8")
    if(length):
        msg = connection.recv(int(length)).decode("utf-8")
        msg=json.loads(msg)
        if(msg["id"]!=2):
            msgs_db[msg["target"]].append(msg)
            print(msg)
            return msg
    return False



def send_msg(msg,connection):
    data = json.dumps(msg)
    message = bytes(data,encoding="utf-8")
    length = len(message)
    length = str(length).encode("utf-8")
    length += b' ' * (HEADER - len(length))
    connection.send(length)
    connection.send(message)


def recieving_end(conn,port):
    while(True):
        rec=recv_msg(conn,port)


def send_end(conn,port):
    send_msg({"msg":"CONNECT_MSG"},conn)
    li=msgs_db[port]
    point=0
    while(True):
        if(point<len(li)):
            send_msg(li[point],conn)
            point+=1
        


l=[]
def server_init():
    res=collection.find({})
    for i in res:
        l.append(i["PORT"])
    return l

available_servers=server_init()
print(available_servers)


def connect_server(*args):
    connection=args[0]
    thread = threading.Thread(target=send_end, args=(connection,args[1]))
    thread.start()

    recv_thread=threading.Thread(target=recieving_end, args=(connection,args[1]))
    recv_thread.start()


    

# Need to store them in a different way ---------------------------------------- 
msgs_db={available_servers[i]:[] for i in range(len(available_servers))}
server_connections=[0 for i in range(len(available_servers))]
for i in range(len(available_servers)):
    server_connections[i]=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_connections[i].connect((HOST,available_servers[i]))


for i in range(len(available_servers)):
    thread = threading.Thread(target=connect_server, args=(server_connections[i],available_servers[i]))
    thread.start()



# while(1):
#     conn,address=server.accept()
#     thread = threading.Thread(target=communicate, args=(conn, address))
#     thread.start()



