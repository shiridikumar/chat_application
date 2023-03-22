from mmap import PROT_READ
import socket
import threading
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
HEADER=64
server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((HOST,PORT))

print("Listening to PORT {} ...".format(PORT))
def communicate(conn,address):
    while(1):
        length=conn.recv(HEADER).decode("utf-8")
        if(length):
            msg = conn.recv(int(length)).decode("utf-8")
            print(msg)
            if(msg)=="exit":
                break
    conn.close()

server.listen()
while(1):
    conn,address=server.accept()
    thread = threading.Thread(target=communicate, args=(conn, address))
    thread.start()






