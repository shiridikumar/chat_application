import socket
import threading
import json
import requests
HOST = ""
PORT = 5000
HEADER = 64
DB_URL = "http://127.0.0.1:8080/server_map"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))


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
        # msg = json.loads(msg)
        # print(msg)
        r = requests.post(url=DB_URL, data=msg)
        data = r.json()
        print(data)

        if(msg) == "exit":
            return False
    return True


def send_end(conn,adress):
    send=send_msg(conn,2,"sending_from_server")

print("Listening to PORT {} ...".format(PORT))
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






