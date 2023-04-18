import socket
import threading
import json
import sys
import requests
import argparse
HOST = "10.1.39.116"

## if central_server run with PORT =10000
PORT = 5000
HEADER = 64
DB_URL = "http://10.1.39.116:8080/server_map"

global redirection_server

parser = argparse.ArgumentParser()
parser.add_argument("-PORT" ,"--port_no", help = "Show Output")
parser.add_argument("-IP","--server",help="Show Output")
args = parser.parse_args()
#need to  Store in a different way -------------------
args.server="10.1.39.116"
global connection_objects
connection_objects={}
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if(args.port_no!=None):
    PORT=args.port_no

global current_outgoing_conns
current_outgoing_conns={}

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
    log("Server {} ,Listening to PORT {} ...".format(HOST,PORT),"succesful")

server_name=HOST+":"+str(PORT)


def communicate_with_server(conn,addr):
    send_msg(conn,0,"SERVER_CONNECT_MSG",0,server_name)
    while(1):
        for i in range(len(current_outgoing_conns[addr])):
            send_msg(conn,current_outgoing_conns[addr][i]["from"],current_outgoing_conns[addr][i]["msg"],current_outgoing_conns[addr][i]["_id"],current_outgoing_conns[addr][i]["server"])
            print("************")
        current_outgoing_conns[addr]=[]

            

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
            connection_objects[m["_id"]]=conn
        elif(m["msg"]=="SERVER_CONNECT_MSG"):
            current_outgoing_conns[server_name]=[]
        else:
            r = requests.post(url=DB_URL, data=msg)
            data = r.json()
            data["msg"]=m["msg"]
            m["server"]=data["server"]
            if(data["server"]!=server_name):
                if(data["server"] not in current_outgoing_conns):
                    newconn=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    ip,port=data["server"].split(":")[0],int(data["server"].split(":")[1])
                    newconn.connect((ip,port))
                    current_outgoing_conns.update({data["server"]:[m]})
                    print("in another server")
                    thread = threading.Thread(target=communicate_with_server, args=(newconn,data["server"]))
                    thread.start()
                else:
                    current_outgoing_conns[data["server"]].append(m)
            
            else:
                send_msg(connection_objects[m["_id"]],m["from"],m["msg"],m["_id"],m["server"])
            
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






