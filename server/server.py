import socket
import threading
import json
import sys
import requests
import argparse
HOST = ""

## if central_server run with PORT =10000
PORT = 5000
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





def send_msg(conn, from_id, msg):
    m = {"id": from_id, "msg": msg}
    data = json.dumps(m)
    message = bytes(data, encoding="utf-8")
    length = len(message)
    length = str(length).encode("utf-8")
    length += b' ' * (HEADER - len(length))
    conn.send(length)
    conn.send(message)


def recv_msg(conn):
    length = conn.recv(HEADER).decode("utf-8")
    if(length):
        msg = conn.recv(int(length)).decode("utf-8")
        print(msg)
        msg=json.loads(msg)
        if(msg["msg"]!="CONNECT_MSG"):
            print(msg,"________________")
            r = requests.post(url=DB_URL, data=msg)
            data = r.json()
            print(data,"******************\n",msg["msg"])

        if(msg) == "exit":
            return False


        
        
    return True


def send_end(conn,adress):
    send=send_msg(conn,2,"sending_from_server")


def communicate(conn,address):
    thread=threading.Thread(target=send_end, args=(conn, address))
    thread.start()

    while(1):
        rec=recv_msg(conn)
        send_msg(conn,2,"recieved_your_message")
        if(rec==False):
            break
    conn.close()


server.listen()

while(1):
    conn,address=server.accept()
    thread = threading.Thread(target=communicate, args=(conn, address))
    thread.start()






