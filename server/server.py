import socket
import threading
import json
import sys
from tkinter.messagebox import NO
import requests
import argparse
HOST = "192.168.255.60"

## if central_server run with PORT =10000
PORT = 5000
HEADER = 64
DB_URL = "http://127.0.0.1:8080/server_map"
global redirection_server

parser = argparse.ArgumentParser()
parser.add_argument("-PORT" ,"--port_no", help = "Show Output")
parser.add_argument("-SERVER","--server",help="Show Output")
args = parser.parse_args()
#need to  Store in a different way -------------------

global connection_objects
connection_objects={}
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if(args.port_no!=None):
    PORT=args.port_no


def log(statement,value=""):
    print(f"[ {statement} ]",end=" ")
    if(value!=""):
        print(f": {value}",end="")
    print()

try:
    if(args.server==None):
        raise ValueError
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



def send_msg(conn, from_id, msg,to,server=""):
    if(server==""):
        server=PORT
    m = {"from": from_id, "msg": msg,"_id":to,"target":server}
    data = json.dumps(m)
    message = bytes(data, encoding="utf-8")
    length = len(message)
    length = str(length).encode("utf-8")
    length += b' ' * (HEADER - len(length))
    # if(server==PORT and to!=1 and to!=2):

    #     print(length,message,data,conn,connection_objects[to])
    conn.send(length)
    conn.send(message)


def recv_msg(conn):
    global redirection_server,connection_objects
    length = conn.recv(HEADER).decode("utf-8")
    if(length):
        msg = conn.recv(int(length)).decode("utf-8")

        m=json.loads(msg)
        if(m["msg"]=="CONNECT_MSG"):
            # send_msg(conn,2,"sending_from_server",1)
            # if(m["_id"]=="643bf84facc4a0e007444aa4"):
            #     print(conn,"this is akanksha")
            connection_objects[m["_id"]]=conn
        if ("target" not in m):
            if(m["msg"]=="SERVER_CONNECT_MSG"):
                redirection_server=conn
            if(m["msg"]!="SERVER_CONNECT_MSG" and m["msg"]!="CONNECT_MSG"):
                r = requests.post(url=DB_URL, data=msg)
                data = r.json()
                data["msg"]=m["msg"]
                send_msg(redirection_server,m["from"],m["msg"],data["_id"],data["server"])
        else:
            if(m["msg"]!="CONNECT_MSG"):
                send_msg(connection_objects[m["_id"]],m["from"],m["msg"],m["_id"])

            


            
        if(msg) == "exit":
            return False

    return True


def send_end(conn,adress):
    send=send_msg(conn,2,"sending_from_server",1)


def communicate(conn,address):
    thread=threading.Thread(target=send_end, args=(conn, address))
    thread.start()

    while(1):
        rec=recv_msg(conn)
        if(rec==False):
            break
    conn.close()


server.listen()

while(1):
    conn,address=server.accept()
    thread = threading.Thread(target=communicate, args=(conn, address))
    thread.start()






