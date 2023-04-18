import eventlet
import socketio
from flask_socketio import SocketIO
from http.client import responses
import json
import flask
from flask import Flask,redirect, url_for, request,render_template,send_file,jsonify
import werkzeug
from werkzeug.utils import secure_filename
from flask import Flask, Response
from flask_cors import CORS,cross_origin
from flask import send_from_directory
from bson import ObjectId
import requests
import pymongo
from pymongo import MongoClient
import socket
import threading
import time

PORT=5000
app=Flask(__name__)
HOST="10.1.39.116"
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app,support_credentials=True)
socketio = socketio(app,cors_allowed_origins="*")
HEADER=64
global current_outgoing_conns
current_outgoing_conns={}
server_name=HOST+":"+str(PORT)
DB_URL = "http://10.1.39.116:8080/server_map"



@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

def communicate_with_server(conn,addr):
    send_msg(conn,0,"SERVER_CONNECT_MSG",0,server_name)
    while(1):
        for i in range(len(current_outgoing_conns[addr])):
            send_msg(conn,current_outgoing_conns[addr][i]["from"],current_outgoing_conns[addr][i]["msg"],current_outgoing_conns[addr][i]["_id"],current_outgoing_conns[addr][i]["server"])
            print("************")
        current_outgoing_conns[addr]=[]

        
def send_msg(client_id, from_id,msg,to,server):
    if(server==""):
        server=PORT
    m = {"from": from_id, "msg": msg,"_id":to,"target":server}
    socketio.emit('output', m, room=client_id)
    print("sending message to client {}".format(client_id))



def recv_msg(conn,m):
    socketio.emit("message",{"akanksha":"i love u shiridi , u can do it "},room=conn)
    # global redirection_server,connection_objects
    # if(m["msg"]=="CONNECT_MSG"):
    #     connection_objects[m["_id"]]=conn
    # elif(m["msg"]=="SERVER_CONNECT_MSG"):
    #     current_outgoing_conns[server_name]=[]
    # else:
    #     r = requests.post(url=DB_URL, data=m)
    #     data = r.json()
    #     data["msg"]=m["msg"]
    #     m["server"]=data["server"]
    #     if(data["server"]!=server_name):
    #         if(data["server"] not in current_outgoing_conns):
    #             newconn=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #             ip,port=data["server"].split(":")[0],int(data["server"].split(":")[1])
    #             newconn.connect((ip,port))
    #             current_outgoing_conns.update({data["server"]:[m]})
    #             print("in another server")
    #             thread = threading.Thread(target=communicate_with_server, args=(newconn,data["server"]))
    #             thread.start()
    #         else:
    #             current_outgoing_conns[data["server"]].append(m)
        
    #     else:
    #         send_msg(connection_objects[m["_id"]],m["from"],m["msg"],m["_id"],m["server"])
        
    return True




@socketio.on('message')
@cross_origin(supports_credentials=True,origin='*')
def handle_message(data):
    print("request came")
    return {"success":"200"}
    


if __name__ == '__main__':
    socketio.run(app,port=5000,host="10.1.39.116")