import socket
import json
import threading
import pymongo
from pymongo import MongoClient

try:
	conn = MongoClient("localhost",27017)
	print("Connected successfully!!!")
except:
	print("Could not connect to MongoDB")

db = conn.users
collection = db.server_mapping

def login():
    ind=1
    l=[]
    res=collection.find({})
    for i in res:
        print(f'{ind} . {i["name"]}')
        ind+=1
        l.append(i)
    log=int(input("\nChoose login : "))
    print("----------------------------------\n")
    return l[log-1]


user=login()
HOST = "192.168.255.51"
PORT = user["server"]
HEADER=64

cli=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
cli.connect((HOST,PORT))

def recv_msg():
    length=cli.recv(HEADER).decode("utf-8")
    if(length):
        msg = cli.recv(int(length)).decode("utf-8")
        msg=json.loads(msg)
        print(msg)
    return True


def send_msg(id,msg):
    m={"_id":id,"msg":msg}
    m["from"]=str(user["_id"])
    data = json.dumps(m)
    message = bytes(data,encoding="utf-8")
    length = len(message)
    length = str(length).encode("utf-8")
    length += b' ' * (HEADER - len(length))
    cli.send(length)
    cli.send(message)


def recieving_end(a,b):
    while(True):
        rec=recv_msg()
        if(rec==False):
            break

sending=True






def message_list(user_id):
    res=collection.find({})
    ind=1
    l=[]
    for i in res:
        if(i["_id"]==user_id):
            continue
        print(f'{ind}. {i["name"]}',end="\t")
        l.append(i)
        ind+=1
    print()
    to=int(input("Choose whom to message : "))
    return l[to-1]

m={"_id":user["_id"],"msg":"connect_msg"}


send_msg(str(user["_id"]),"CONNECT_MSG")
thread = threading.Thread(target=recieving_end, args=(1,2))
thread.start()
while(sending):
    to=message_list(user["_id"])
    inp=input("Enter a new message : ")
    send_msg(str(to["_id"]),inp)
    if(inp=="exit"):
        break





