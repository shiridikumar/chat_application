import eventlet
import gevent
import socketio
from flask_socketio import SocketIO
from flask_socketio import join_room, leave_room    
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
import argparse
import threading

parser = argparse.ArgumentParser()
parser.add_argument("-PORT" ,"--port_no", help = "Show Output")
parser.add_argument("-IP","--server",help="Show Output")
args = parser.parse_args()
#need to  Store in a different way -------------------
args.server="172.18.0.1"
PORT=5050


conn = MongoClient("localhost",27017)
db = conn.users


HOST="172.18.0.1"
try:
    if(args.server==None):
        raise ValueError
    PORT=int(PORT)
except :
    print(f"Failed to connect")

else:
    print("Server {} ,Listening to PORT {} ...".format(HOST,PORT),"succesful")



app=Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app,support_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*",async_handlers=True, pingTimeout=900)
HEADER=64
global current_outgoing_conns
current_outgoing_conns={}
server_name=HOST+":"+str(PORT)
DB_URL = "http://172.18.0.1:8080/server_map"



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
    #             print("in another server")Notifications
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
    # recv_msg(request.sid,data)
    print(data)
    from_=data["from"]
    to=data["to"]
    chatname=sorted([from_,to])
    chathis=db.chats.find_one({"chatname":chatname})
    if(chathis!=None):
        chathis["history"].append(data)
        db.chats.update_one({"chatname":chatname},{ "$set": { 'history': chathis["history"] } })
    else:
        chathis={"history":[data],"chatname":chatname}
        db.chats.insert_one(chathis)
    
    # socketio.emit("message",chathis,room=conn)

    return {"success":"200"}
    


@app.route("/fetchchat",methods=["POST"])
@cross_origin(supports_credentials=True,origin='*')
def fetchchat():
    data =json.loads(request.data)
    print(data,"*************")
    user=data["user"]
    chat=data["chat"]
    chatname=sorted([user,chat])
    chats=db.chats.find_one({"chatname":chatname})
    if(chats==None):
        chats={"history":[]}
    return {"chats":chats["history"]}


#-----------------Group chat---------------------

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', to=room)

@socketio.on('grpmessage')
@cross_origin(supports_credentials=True,origin='*')
def handle_message(data):
    # recv_msg(request.sid,data)
    print(data)
    grpid=data["grpid"]
    grp=db.grp.find_one({"grpid":grpid})
    if(grp!=None):
        grp["history"].append(data)
        db.grp.update_one({"grpid":grpid},{ "$set": { 'history': grp["history"] } })
    else:
        return {"Group not found":"404"}
    
    return {"success":"200"}

@app.route("/fetchgrp", methods=["POST"])
@cross_origin(supports_credentials=True,origin='*')
def fetchgrp():
    data =json.loads(request.data)
    print(data,"###############")
    user=data["user"]
    grp=data["grp"]
    chats=db.grp.find_one({"grpname":grp})
    if(chats==None):
        chats={"history":[]}
    return {"chats":chats["history"]}


if __name__ == '__main__':
    socketio.run(app,port=PORT,host=HOST)