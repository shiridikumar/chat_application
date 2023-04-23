from locale import D_T_FMT
from multiprocessing import connection
from tkinter.tix import Tree
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
global redirection_server
import threading
import datetime
from dotenv import load_dotenv
load_dotenv()
from flask_socketio import send, emit, join_room, leave_room, close_room, rooms


parser = argparse.ArgumentParser()
parser.add_argument("-PORT" ,"--port_no", help = "Show Output")
parser.add_argument("-IP","--server",help="Show Output")
args = parser.parse_args()
#need to  Store in a different way -------------------
# args.server="10.1.39.116"
global connection_objects
connection_objects={}
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if(args.port_no!=None):
    PORT=args.port_no

HOST=None
PORT=5000
try:
    if(args.server==None):
        args.server="10.1.39.116"
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

global group_chats
group_chats={}

global grp_connections
grp_connections={}

conn = MongoClient("localhost",27017)
db = conn.users

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response




def find_key(sid):
    for i in connection_objects:
        # print(i,connection_objects[i])
        if(connection_objects[i]==sid):
            return i


def recv_msg(m,email,ind):
    global redirection_server,connection_objects,current_outgoing_conns
    print(connection_objects,"****************")
    
    if(email in connection_objects):
        #("already present in connection objects")
        socketio.emit("message",{"from":m["from"],"to":m["to"],"msg":m["msg"],"time":m["time"],"seen":0},room=connection_objects[email])
        if("from_server" in m):
            requests.post("http://{}/send_deliver".format(m["from_server"]),data=json.dumps({"from":m["to"],"to":m["from"],"ind":ind}))
        else:
            chatname=sorted([m["to"],m["from"]])
            his=db.chats.find_one({"chatname":chatname})
            chathis=his["history"]
            chathis[ind]["seen"]=1
            ret=db.chats.find_one_and_update({"chatname":chatname},{"$set":{"history":chathis}},return_document=True)
            ret.pop("_id")
            requests.post(url=CENTRAL_SERVER+str("/update_central_data"),data=json.dumps(ret))
            socketio.emit("delivered",{"from":m["to"],"chat_ind":[ind]},room=connection_objects[email])


    else:
        # #(m,"*******************************"
        r = requests.post(url=DB_URL, data=json.dumps(m))
        data = r.json()
        #("***********************",data,"__________________________")

        if(data["server"]!=server_name):
            ob={"data":m,"from_server":server_name}
            req=requests.post(url=f'http://{data["server"]}/send_from_server',data=json.dumps(ob))
        else:
            print("user offline *****************************")
    return True


@socketio.on('disconnect')
@cross_origin(supports_credentials=True,origin='*')
def handle_disconnect():
    global updated_chats,connection_objects
    email=find_key(request.sid)
    res=db.chats.find({"chatname": { "$in": [email] } },{"_id":0})
    #(updated_chats)
    upds=[]
    for  i in res:
        if tuple(i["chatname"]) in updated_chats:
            # #(i["chatname"],"*************************************")
            upds.append(i)
    data={"updated":upds}
    print(email,"_____________________")
    if(email in connection_objects):
        print("succesfully removed")
        connection_objects.pop(email)
        print(connection_objects)

        
    ret=db.users.find_one_and_update({"email":email},{"$set":{"lastseen":str(datetime.datetime.now())}},{"_id":0})
    # requests.post(url=CENTRAL_SERVER+str("/update_central_data"),data=json.dumps(ret))
    
    #(len(upds),"***************")
    # r = requests.post(url=CENTRAL_SERVER+str("/backup_data"),data=json.dumps(data))
    print(request.sid,"_______________","Disconnected")
    return {200:2000}


@socketio.on('message')
@cross_origin(supports_credentials=True,origin='*')
def handle_message(data):
    global updated_chats
    from_=data["from"]
    to=data["to"]
    data["seen"]=0
    # data["time"]=datetime.datetime.now()
    chatname=sorted([from_,to])
    chathis=db.chats.find_one({"chatname":chatname})
    updated_chats[tuple(chatname)]=1
    ind=0
    if(chathis!=None):
        chathis["history"].append(data)
        print(chathis,"********")
        ind=len(chathis["history"])-1
        ret=db.chats.find_one_and_update({"chatname":chatname},{ "$set": { 'history': chathis["history"] }},return_document=True)
        # print(len(ret["history"]),"_________________",len(chathis["history"]))
      
        ret.pop("_id")
        requests.post(url=CENTRAL_SERVER+str("/update_central_data"),data=json.dumps(ret))
    else:
        chathis={"history":[data],"chatname":chatname}
        db.chats.insert_one(chathis)
        print(chathis)
        requests.post(url=CENTRAL_SERVER+str("/insert_central_data"),data=json.dumps(chathis))
        ind=len(chathis["history"])-1


    recv_msg(data,data["to"],ind)
    
    # socketio.emit("message",chathis,room=conn)

    return {"success":"200"}
    


@socketio.on('connectclient')
@cross_origin(supports_credentials=True,origin='*')
def handle_connect(data):
    global connection_objects
    connection_objects[data["email"]]=request.sid
    ret=db.users.find_one_and_update({"email":data["email"]},{"$set":{"lastseen":"online"}},{"_id":0})
    # requests.post(url=CENTRAL_SERVER+str("/update_central_data"),data=json.dumps(ret))
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
            if(chathis[j]["from"]!=other):
                j-=1
                continue
            if(chathis[j]["seen"]==1 or chathis[j]["seen"]==2):
                break
            else:
                chathis[j]["seen"]=1
            j-=1
        ret=db.chats.find_one_and_update({"chatname":i["chatname"]},{"$set":{"history":chathis}},return_document=True)
        ret.pop("_id")
        requests.post(url=CENTRAL_SERVER+str("/update_central_data"),data=json.dumps(ret))
        updated_chats[tuple(i["chatname"])]=1
        
        


        

        

    # #(updated_chats)


    return {"200":"2000"}

@app.route("/update_ticks",methods=["POST"])
@cross_origin(supports_credentials=True,origin='*')
def update_ticks():
    global connection_objects
    data=json.loads(request.data)
    target=data["from"]
    data=data["updates"]
    #(data,"****************************************************************")
    for i in data:
        email=i
        if i in connection_objects:
            socketio.emit("delivered",{"from":target,"chat_ind":data[i]},room=connection_objects[i])
    return {200:200}
    
@app.route("/send_deliver",methods=["POST"])
@cross_origin(supports_credentials=True,origin='*')
def send_deliver():
    global connection_objects
    data=json.loads(request.data)
    target=data["from"]
    chatname=sorted([data["frrom"],data["to"]])
    ob=db.chats.find_one({"chatname":chatname})
    his=ob["history"]
    his[data["ind"]]["seen"]=1
    ret=db.chats.find_one_and_update({"chatname":chatname},{"$set":{"history":his}},return_document=True)
    ret.pop("_id")
    requests.post(url=CENTRAL_SERVER+str("/update_central_data"),data=json.dumps(ret))
    # updated_chats[tuple(chatname)]=1
    if(data["to"] in connection_objects):
        socketio.emit("delivered",{"from":target,"chat_ind":[data["ind"]]},room=connection_objects[data["to"]])
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
    #(target)
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
    #(data,"+++++++++++++++++++++++++++")
    data=data["data"]
    if(from_server!=HOST):
        from_=data["from"]
        to=data["to"]
        chatname=sorted([from_,to])
        chathis=db.chats.find_one({"chatname":chatname})
        updated_chats[tuple(chatname)]=1
        ind=0
        if(chathis!=None):
            chathis["history"].append(data)
            ind=len(chathis["history"])-1
            ret=db.chats.find_one_and_update({"chatname":chatname},{ "$set": { 'history': chathis["history"] } },return_document=True)
            ret.pop("_id")
            requests.post(url=CENTRAL_SERVER+str("/update_central_data"),data=json.dumps(ret))
        else:
            chathis={"history":[data],"chatname":chatname}
            ind=len(chathis["history"])-1
            db.chats.insert_one(chathis)
            print(chathis)
            requests.post(url=CENTRAL_SERVER+str("/insert_central_data"),data=json.dumps(chathis))
    
    recv_msg(data,data["to"],ind)
        
    return {2000:2000}


@app.route("/userdata",methods=["POST"])
@cross_origin(supports_credentials=True,origin='*')
def userdata():
    data=json.loads(request.data);
    #(request.data);
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

    grp_list = db.grp.find({"members":{"$in":[email]}})
    for i in grp_list:
        contacts.append(i["name"]) 
        lastmessage.append(i["history"][-1]["msg"])
    
    print(lastmessage,contacts,"*********************") 
    # lastmessage.reverse()
    # contacts.rev

    return {"lastmessage":lastmessage[::-1],"contacts":contacts[::-1]}

@app.route("/add_group",methods=["POST"])
@cross_origin(supports_credentials=True,origin='*')
def add_group():
    data=json.loads(request.data)
    print(data)
    if(HOST!=CENTRAL_SERVER.split(":")[0]):
        db.grp.insert_one(data)


@app.route("/update_group",methods=["POST"])
@cross_origin(supports_credentials=True,origin='*')
def a_group():
    data=json.loads(request.data)
    print(data)
    if(HOST!=CENTRAL_SERVER.split(":")[0]):
        db.grp.find_one_and_update({"name":data["name"]},{"$set":data})

@app.route("/test",methods=["POST"])
@cross_origin(supports_credentials=True,origin='*')
def test():
    return {"working":1}

#-----------------Group chat---------------------

# def recv_grp_msg(m,id):
#     global redirection_server, grp_connections
#     if(id in grp_connections):
#         socketio.emit("grpmessage",{"from":m["from"],"msg":m["msg"]},room=grp_connections[id])

#     else:
#         # print(m,"*******************************")
#         r = requests.post(url=DB_URL, data=json.dumps(m))
#         data = r.json()
#         print(data,"__________________________")

#         if(data["server"]!=server_name):
#             ob={"data":m,"from_server":server_name}
#             req=requests.post(url=f'http://{data["server"]}/send_from_server',data=json.dumps(ob))
#         # else:

#         #     send_msg(connection_objects[m["_id"]],m["from"],m["msg"],m["_id"],m["server"])
        
#     return True


# @socketio.on('grpmessage')
# @cross_origin(supports_credentials=True,origin='*')
# def handle_message(data):
#     global group_chats
#     print("*************************came")
#     recv_grp_msg(data,data["grpid"])

#     print(request.sid,"_______________")
#     print(data)
#     id = data["grpid"]
#     find_grp=db.grp.find_one({"_id":id})
#     group_chats[id]=1
#     if(find_grp!=None):
#         db.grp.update_one({"_id":id},{"$push":{"history":data}})

#     return {"success":"200"}


# def on_join(data,sid):
#     email = data["from"]
#     us=db.grp.find_one({"name":"group "+data["grpid"]})
#     join_room(data["grpid"])
#     print("joined room",data["grpid"])
#     if(data["from"] not in us["members"]):
#         ret=db.grp.find_one_and_update({"_id":ObjectId(data["grpid"])},{"$push":{"members":email}},return_document=True)
#         ret.pop("_id")
#         print(data["grpid"],"__________________________________",type(data["grpid"]))
#         socketio.emit("joingrp",{"grpid":str(data["grpid"]),"last":f'{email} has entered the room.' ,"to":email} , room=data["grpid"])
#         ms=f'{email} has entered the room.'
#         ret=db.grp.find_one_and_update({"name":"group "+data["grpid"]},{"$push":{"history":{"from":data["from"],"msg":ms}}},return_document=True)
#         ret.pop("_id")

#     print(data)

# @socketio.on('join')
# def join(data):
#     # if("msg" in data):
#     #     email=data["from"]
#     #     msg=data["msg"]
#     #     # db.grp.update_one({"_id":ObjectId(data["grpid"])},{"$push":{"history":{"from":data["from"],"msg":msg}}})
#     #     socketio.emit("grpmessage",{"grpid":str(data["grpid"])} , room=data["grpid"])
#     # else:
#     if data["grpid"] == "":
#         data["grpid"]=str(db.grp.insert_one({"history":[],"members":[]}).inserted_id)
#         ret=db.grp.find_one_and_update({"_id":ObjectId(data["grpid"])},{"$set":{"name":"group "+str(data["grpid"])}},return_document=True)
#         ret.pop("_id")
#         requests.post(f'http://{CENTRAL_SERVER}/add_group',data=json.dumps({"grpid":data["grpid"]}))
#     on_join(data,request.sid)


# @socketio.on('leave')
# def on_leave(data):
#     email = data["from"]
#     room = data["grpid"]
#     leave_room(room)
    
#     db.grp.update_one({"_id":ObjectId(room)},{"$pull":{"members":email}})
#     send(email + ' has left the room.', to=room)

#     if len(db.grp.find_one({"_id":ObjectId(room)})["members"]) == 0:
#         db.grp.delete_one({"_id":ObjectId(room)})
#         close_room(room)

#     # return {"success":"200"}
    
# def send_msg(data):
#     email=data["from"]
#     msg=data["msg"]
#     print(data["grpid"],"??????????????????????????????????",data)
#     socketio.emit("grpmessage",{"grpid":str(data["grpid"]),"msg":msg ,"from":email} , room=data["grpid"])
#     # socketio.emit("joingrp",{"grpid":str(data["grpid"]),"last":f'{email} has entered the room.' ,"to":email} , room="64445aa4b6e2d0bf606b7c4a")
#     # ms=f'{email} has entered the room.'
#     ret=db.grp.find_one_and_update({"name":"group "+data["grpid"]},{"$push":{"history":{"from":data["from"],"msg":msg}}},return_document=True)
#     ret.pop("_id")
#     requests.post("http://")




# @socketio.on('grpmessage')
# def on_message(data):
#     send_msg(data)
#     return {200:200}


# # @app.route("/addtogrp", methods=["POST"])
# # @cross_origin(supports_credentials=True,origin='*')
# # def addtogrp():
# #     data=json.loads(data)
# #     print(data)
# #     db.grp.update_one({"_id":ObjectId(data["grpid"])},{"$push":{"members":data["email"]}})






# @app.route("/fetchgrp", methods=["POST"])
# @cross_origin(supports_credentials=True,origin='*')
# def fetchgrp():
#     data=json.loads(request.data)
#     print(data)
#     id=data["grpid"]
#     id=id[6:]
#     print(id,"***********************")
#     find_grp=db.grp.find_one({"_id":ObjectId(id)})
#     if(find_grp==None):
#         return {"history":[]}
#     return {"history":find_grp["history"]}

if __name__ == '__main__':
    socketio.run(app,port=PORT,host=HOST)