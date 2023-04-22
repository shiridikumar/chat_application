from locale import D_T_FMT
from multiprocessing import connection
import eventlet
import gevent
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
import os
import argparse
import threading
import datetime
from dotenv import load_dotenv
load_dotenv()


parser = argparse.ArgumentParser()
parser.add_argument("-PORT" ,"--port_no", help = "Show Output")
parser.add_argument("-IP","--server",help="Show Output")
args = parser.parse_args()
if(args.server==None):
    args.server="10.1.39.116"
if(args.port_no==None):
    args.port_no=5000

HOST=None
PORT=5000
try:
    if(args.server==None):
        raise ValueError
    if(args.port_no!=None):
        PORT=int(args.port_no)
    if(args.server!=None):
        HOST=args.server
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
CENTRAL_SERVER=os.getenv("CENTRAL_SERVER")
DB_URL = "http://10.1.39.116:8080/server_map"


global updated_chats
updated_chats={}

conn = MongoClient("localhost",27017)
db = conn.users
global connection_objects
connection_objects={}
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response




def find_key(sid):
    for i in connection_objects:
        if(connection_objects[i]==sid):
            return i


def recv_msg(m,email):
    global redirection_server,connection_objects,current_outgoing_conns
    print(connection_objects,"****************")
    
    if(email in connection_objects):
        print("already present in connection objects")
        socketio.emit("message",{"from":m["from"],"to":m["to"],"msg":m["msg"],"time":m["time"],"seen":0},room=connection_objects[email])

    else:
        # print(m,"*******************************"
        r = requests.post(url=DB_URL, data=json.dumps(m))
        data = r.json()
        print("***********************",data,"__________________________")

        if(data["server"]!=server_name):
            ob={"data":m,"from_server":server_name}
            req=requests.post(url=f'http://{data["server"]}/send_from_server',data=json.dumps(ob))
        # else:

        #     send_msg(connection_objects[m["_id"]],m["from"],m["msg"],m["_id"],m["server"])
        
    return True


@socketio.on('disconnect')
@cross_origin(supports_credentials=True,origin='*')
def handle_disconnect():
    global updated_chats
    email=find_key(request.sid)
    res=db.chats.find({"chatname": { "$in": [email] } },{"_id":0})
    print(updated_chats)
    upds=[]
    for  i in res:
        if tuple(i["chatname"]) in updated_chats:
            # print(i["chatname"],"*************************************")
            upds.append(i)
    data={"updated":upds}
    # ls=str(datetime.datetime.now())
    # print(ls)
    # d=datetime.datetime.strptime(ls,"%Y-%m-%dT%H:%M:%S.000Z")
    # print(d)
    db.users.find_one_and_update({"email":email},{"$set":{"lastseen":str(datetime.datetime.now())}})
    print(len(upds),"***************")
    r = requests.post(url=CENTRAL_SERVER+str("/backup_data"),data=json.dumps(data))
    print(request.sid,"_______________","Disconnected")
    return {200:2000}


@socketio.on('message')
@cross_origin(supports_credentials=True,origin='*')
def handle_message(data):
    global updated_chats
    recv_msg(data,data["to"])
    from_=data["from"]
    to=data["to"]
    data["seen"]=0
    # data["time"]=datetime.datetime.now()
    chatname=sorted([from_,to])
    chathis=db.chats.find_one({"chatname":chatname})
    updated_chats[tuple(chatname)]=1
    if(chathis!=None):
        chathis["history"].append(data)
        db.chats.update_one({"chatname":chatname},{ "$set": { 'history': chathis["history"] } })
    else:
        chathis={"history":[data],"chatname":chatname}
        db.chats.insert_one(chathis)
    
    # socketio.emit("message",chathis,room=conn)

    return {"success":"200"}
    


@socketio.on('connectclient')
@cross_origin(supports_credentials=True,origin='*')
def handle_connect(data):
    global connection_objects
    connection_objects[data["email"]]=request.sid
    db.users.find_one_and_update({"email":data["email"]},{"$set":{"lastseen":"online"}})
    res=db.chats.find({"chatname": { "$in": [data["email"]] } },{"_id":0})
    chat_ticks={}
    for i in res:
        other=i["chatname"][0]
        if(other==data["email"]):
            other=i["chatname"][1]
        l=[]
        chathis=i["history"]
        j=len(chathis)-1
        while(j>=0):
            if(chathis[j]["seen"]==1 or chathis[j]["seen"]==2):
                break
            else:
                chathis[j]["seen"]=1
            j-=1
        db.chats.find_one_and_update({"chatname":i["chatname"]},{"$set":{"history":chathis}})
        
        


        

        

    # print(updated_chats)


    return {"200":"2000"}

@app.route("/update_ticks",methods=["POST"])
@cross_origin(supports_credentials=True,origin='*')
def update_ticks():
    global connection_objects
    data=json.loads(request.data)
    target=data["from"]
    data=data["updates"]
    print(data,"****************************************************************")
    for i in data:
        email=i
        if i in connection_objects:
            socketio.emit("delivered",{"from":target,"chat_ind":data[i]},room=connection_objects[i])
    return {200:200}
    
    








@app.route("/fetchchat",methods=["POST"])
@cross_origin(supports_credentials=True,origin='*')
def fetchchat():
    data =json.loads(request.data)
    user=data["user"]
    chat=data["chat"]
    chatname=sorted([user,chat])
    chats=db.chats.find_one({"chatname":chatname})
    lastseen=None
    target=db.users.find_one({"email":chat})
    print(target)
    if(target):
        lastseen=target["lastseen"]
    if(chats==None):
        chats={"history":[]}
    return {"chats":chats["history"],"lastseen":lastseen}


@app.route("/send_from_server",methods=["POST"])
@cross_origin(supports_credentials=True,origin='*')
def send_from_server():
    global updated_chats
    data=json.loads(request.data)
    from_server=data["from_server"].split(":")[0]
    print(data,"+++++++++++++++++++++++++++")
    data=data["data"]
    recv_msg(data,data["to"])
    if(from_server!=HOST):
        from_=data["from"]
        to=data["to"]
        chatname=sorted([from_,to])
        chathis=db.chats.find_one({"chatname":chatname})
        updated_chats[tuple(chatname)]=1
        if(chathis!=None):
            chathis["history"].append(data)
            db.chats.update_one({"chatname":chatname},{ "$set": { 'history': chathis["history"] } })
        else:
            chathis={"history":[data],"chatname":chatname}
            db.chats.insert_one(chathis)
        
    return {2000:2000}


@app.route("/userdata",methods=["POST"])
@cross_origin(supports_credentials=True,origin='*')
def userdata():
    data=json.loads(request.data);
    print(request.data);
    email=data["email"]
    res=db.chats.find({"chatname": { "$in": [email] } })
    contacts=[]
    lastmessage=[]
    for i in res:
        cont=i["chatname"][0]
        if(i["chatname"][0]==email):
            cont=i["chatname"][1]
        if(cont!=""):
            contacts.append(cont)
            lastmessage.append(i["history"][-1]["msg"])
    print(lastmessage,contacts) 
    # lastmessage.reverse()
    # contacts.rev

    return {"lastmessage":lastmessage[::-1],"contacts":contacts[::-1]}



if __name__ == '__main__':
    socketio.run(app,port=PORT,host=HOST)