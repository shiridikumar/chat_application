from pickle import TRUE
import socket
HOST = "127.0.1.1"
PORT = 5050
HEADER=64

cli=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
cli.connect((HOST,PORT))
def send_msg(msg):
    message = msg.encode("utf-8")
    length = len(message)
    length = str(length).encode("utf-8")
    length += b' ' * (HEADER - len(length))
    cli.send(length)
    print(message)
    cli.send(message)


sending=True
print("Enter 'exit' for disconnecting")
while(sending):
    inp=input("Enter a new message : ")
    send_msg(inp)
    if(inp=="exit"):
        break