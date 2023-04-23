from http.client import responses
import json
from multiprocessing import dummy
import flask
from flask import Flask, redirect, url_for, request, render_template, send_file, jsonify
import werkzeug
from werkzeug.utils import secure_filename
from flask import Flask, Response
from flask_cors import CORS, cross_origin
from flask import send_from_directory
from bson import ObjectId
import requests
import pymongo
from pymongo import MongoClient
from Consistenthashing import ConsistentHashing
from flask_socketio import SocketIO
from flask_socketio import send, emit, join_room, leave_room, close_room, rooms

PORT = 8080
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, support_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*",async_handlers=True, pingTimeout=900)

conn = MongoClient("localhost", 27017)
db = conn.users
# db.server_mapping = db.server_mapping
servers = ["server1","server2"]  # ,"server2"]
server_addr = {"server1":"10.1.39.116:5000","server2":"10.42.0.37"}#,"server2":"10.42.0.37:5000"}

backup_servers=["server3"]
backup_addr={"server3":"10.1.39.116:6000"}
consistent_hashing = ConsistentHashing(servers)

def update_ticks(data,email):
    serv_tikcs={server_addr[i]:{} for i in servers}
    for i in data:
        serv_name=db.server_mapping.find_one({"email":i},{"_id":0})
        if(serv_name):
            serv_name=serv_name["server"]
            serv_tikcs[serv_name].update({i:data[i]})
    for i in serv_tikcs:
        print(serv_tikcs,"????????????????")
        requests.post("http://{}/update_ticks".format(i),data=json.dumps({"updates":serv_tikcs[i],"from":email}))


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


@app.route("/signin", methods=["POST"])
@cross_origin(supports_credentials=True, origin='*')
def signin():
    data = json.loads(request.data)
    email = data["email"]
    password = data["password"]
    user = db.users.find_one({"email": email})
    if(user == None):
        db.users.insert_one(
            {"email": email, "password": password, "chats": [], "lastseen": ""})
        user = db.users.find_one({"email": email})
        serv = consistent_hashing.get_server(str(user["_id"]))
        print(serv, "________________________")
        db.server_mapping.insert_one(
            {"email": email, "server": server_addr[serv], "server_name": serv})
    else:
        print(user)
        user = db.users.find_one({"email": email})
        serv = consistent_hashing.get_server(str(user["_id"]))
        print(serv, "________________________")
        {"$set": {'server': server_addr[serv], 'server_name': serv}}
        db.server_mapping.find_one_and_update(
            {"email": email}, {"$set": {'server': server_addr[serv], 'server_name': serv}})
    res = db.chats.find({"chatname": {"$in": [email]}})
    contacts = []
    lastmessage = []
    chat_ticks = {}
    for i in res:
        cont = i["chatname"][0]
        if(i["chatname"][0] == email):
            cont = i["chatname"][1]
        contacts.append(cont)
        lastmessage.append(i["history"][-1]["msg"])
        other=cont
        l=[]
        chathis = i["history"]
        j = len(chathis)-1
        while(j >= 0):
            if(chathis[j]["to"]!=email):
                j-=1
                continue
            if(chathis[j]["seen"] == 1 or chathis[j]["seen"] == 2):
                break
            else:
                chathis[j]["seen"] = 1
            l.append(j)
            j -= 1
        chat_ticks.update({other: l})
        db.chats.find_one_and_update({"chatname":i["chatname"]},{"$set":{"history":chathis}})
    print(chat_ticks,"??????????????????????????????????????????????","needto_be updated")
    update_ticks(chat_ticks,email)

    print(lastmessage, contacts)

    return {"server_name": serv, "server": server_addr[serv], "last": lastmessage, "contacts": contacts}


@app.route("/backup_data", methods=["POST"])
@cross_origin(supports_credentials=True, origin='*')
def backup_data():
    data = request.data
    data = json.loads(data)["updated"]
    for i in data:
        doc = db.chats.find_one_and_update({"chatname": i["chatname"]}, {
                                           "$set": {'history': i["history"]}})
    print(data, "___________________________")
    return {200: 200}


@app.route("/server_map", methods=["POST"])
@cross_origin(supports_credentials=True, origin='*')
def server_map():
    data = request.data
    print(request)
    data = json.loads(data)
    print(data)
    if(data["msg"] != "CONNECT_MSG"):
        user = db.server_mapping.find_one({"email": data["to"]})
        print(user, ",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")
        if(user):
            user["_id"] = str(user["_id"])
        else:
            db.users.insert_one(
                {"email": data["to"], "password": "password", "chats": [], "lastseen": ""})
            user = db.users.find_one({"email": data["to"]})
            user["_id"] = str(user["_id"])
            serv = consistent_hashing.get_server(str(user["_id"]))
            db.server_mapping.insert_one(
                {"email": data["to"], "server": server_addr[serv], "server_name": serv})
            user = db.server_mapping.find_one({"email": data["to"]})
            user["_id"] = str(user["_id"])

        print(user, ",,,,,,,,,,,,,,,")
        return user
    return {1: 1}

@app.route("/fetchchat", methods=["POST"])
@cross_origin(supports_credentials=True, origin='*')
def fetchchat():
    data = json.loads(request.data)
    user = data["user"]
    chat = data["chat"]
    print(user, chat)
    chatname = sorted([user, chat])
    chats = db.chats.find_one({"chatname": chatname})
    print(chats)

@app.route("/update_central_data", methods=["POST"])
@cross_origin(supports_credentials=True, origin='*')
def update_data():
    data=json.loads(request.data)
    print(data,"?????????????????????????")
    print(data["chatname"])
    db.chats.find_one_and_update({"chatname":data["chatname"]},{"$set":{"history":data["history"]}})
    print("succesfully updated")
    return {200:200}


@app.route("/insert_central_data", methods=["POST"])
@cross_origin(supports_credentials=True, origin='*')
def insert_data():
    data=json.loads(request.data)
    db.chats.insert_one(data)
    return {200:200}

def recv_grp_msg(m,id):
    global redirection_server, grp_connections
    if(id in grp_connections):
        socketio.emit("grpmessage",{"from":m["from"],"msg":m["msg"]},room=grp_connections[id])

    else:
        # print(m,"*******************************")
        r = requests.post(url=DB_URL, data=json.dumps(m))
        data = r.json()
        print(data,"__________________________")

        if(data["server"]!=server_name):
            ob={"data":m,"from_server":server_name}
            req=requests.post(url=f'http://{data["server"]}/send_from_server',data=json.dumps(ob))
        # else:

        #     send_msg(connection_objects[m["_id"]],m["from"],m["msg"],m["_id"],m["server"])
        
    return True


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


def on_join(data,sid):
    email = data["from"]
    us=db.grp.find_one({"name":"group "+data["grpid"]})
    join_room(data["grpid"])
    print("joined room",data["grpid"])
    if(data["from"] not in us["members"]):
        ret=db.grp.find_one_and_update({"name":"group "+data["grpid"]},{"$push":{"members":email}},return_document=True)
        ret.pop("_id")
        print(data["grpid"],"__________________________________",type(data["grpid"]))
        socketio.emit("joingrp",{"grpid":str(data["grpid"]),"last":f'{email} has entered the room.' ,"to":email} , room=data["grpid"])
        ms=f'{email} has entered the room.'
        ret=db.grp.find_one_and_update({"name":"group "+data["grpid"]},{"$push":{"history":{"from":data["from"],"msg":ms}}},return_document=True)
        ret.pop("_id")
        for i in server_addr:
            requests.post(f'http://{server_addr[i]}/update_group',data=json.dumps(ret))
    print(data)


@socketio.on('join')
def join(data):
    if data["grpid"] == "":
        data["grpid"]=str(db.grp.insert_one({"history":[],"members":[]}).inserted_id)
        ret=db.grp.find_one_and_update({"_id":ObjectId(data["grpid"])},{"$set":{"name":"group "+str(data["grpid"])}},return_document=True)
        ret.pop("_id")
        for i in server_addr:
            requests.post(f'http://{server_addr[i]}/add_group',data=json.dumps(ret))
    on_join(data,request.sid)


@socketio.on('leave')
def on_leave(data):
    email = data["from"]
    room = data["grpid"]
    leave_room(room)
    
    db.grp.update_one({"_id":ObjectId(room)},{"$pull":{"members":email}})
    send(email + ' has left the room.', to=room)

    if len(db.grp.find_one({"_id":ObjectId(room)})["members"]) == 0:
        db.grp.delete_one({"_id":ObjectId(room)})
        close_room(room)

    # return {"success":"200"}
    
def send_msg(data):
    email=data["from"]
    msg=data["msg"]
    print(data["grpid"],"??????????????????????????????????",data)
    socketio.emit("grpmessage",{"grpid":str(data["grpid"]),"msg":msg ,"from":email} , room=data["grpid"])
    # socketio.emit("joingrp",{"grpid":str(data["grpid"]),"last":f'{email} has entered the room.' ,"to":email} , room="64445aa4b6e2d0bf606b7c4a")
    # ms=f'{email} has entered the room.'
    ret=db.grp.find_one_and_update({"name":"group "+data["grpid"]},{"$push":{"history":{"from":data["from"],"msg":msg}}},return_document=True)
    ret.pop("_id")
    for i in server_addr:
        requests.post(f'http://{server_addr[i]}/update_group',data=json.dumps(ret))


@socketio.on('grpmessage')
def on_message(data):
    send_msg(data)
    return {200:200}


# @app.route("/addtogrp", methods=["POST"])
# @cross_origin(supports_credentials=True,origin='*')
# def addtogrp():
#     data=json.loads(data)
#     print(data)
#     db.grp.update_one({"_id":ObjectId(data["grpid"])},{"$push":{"members":data["email"]}})






@app.route("/fetchgrp", methods=["POST"])
@cross_origin(supports_credentials=True,origin='*')
def fetchgrp():
    data=json.loads(request.data)
    print(data)
    id=data["grpid"]
    id=id[6:]
    print(id,"***********************")
    find_grp=db.grp.find_one({"_id":ObjectId(id)})
    if(find_grp==None):
        return {"history":[]}
    return {"history":find_grp["history"]}

@app.route("/server_failure", methods=["POST"])
@cross_origin(supports_credentials=True,origin='*')
def server_failure():
    data=json.loads(request.data)
    serv=data["server"]
    print(data,"************************")
    addr=[]
    for i in server_addr:
        addr.append(server_addr[i])

    if(serv in addr):
        try :
            requests.post("http://{}/test".format(serv),data={"1":"1"})
        except:
            print("failing" ,"*********************************")
            consistent_hashing.add_server(backup_servers[0])
            for i in server_addr:
                if(data["server"]==server_addr[i]):
                    consistent_hashing.remove_server(i)
                    server_addr.pop(i)
                    break
        
            return {"newserver":backup_addr[backup_servers[0]]}
        else:
            return {200:200}
    return {"newserver":backup_addr[backup_servers[0]]}



if __name__ == "__main__":
    # app.run(debug=True, port=8080, host="10.1.39.116")
    socketio.run(app,port=PORT,host="10.1.39.116")
