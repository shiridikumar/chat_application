from pickle import TRUE
import socket
import json
import threading

HOST = "127.0.0.1"
PORT = 5000
HEADER=64

cli=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
cli.connect((HOST,PORT))

def recv_msg():
    length=cli.recv(HEADER).decode("utf-8")
    if(length):
        msg = cli.recv(int(length)).decode("utf-8")
        msg=json.loads(msg)
        print(msg["msg"],msg["id"])
    return True



def send_msg(id,msg):
    m={"id":id,"msg":msg}
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
m={"id":0,"msg":"connect_msg"}
send_msg(1,"CONNECT_MSG")

thread = threading.Thread(target=recieving_end, args=(1,2))
thread.start()
while(sending):
    
    inp=input("Enter a new message : ")
    send_msg(1,inp)
    if(inp=="exit"):
        break
