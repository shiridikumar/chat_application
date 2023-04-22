from http.client import responses
import json
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

PORT = 8080
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, support_credentials=True)


conn = MongoClient("localhost", 27017)
db = conn.users
# db.server_mapping = db.server_mapping
servers = ["server1"]#,"server2"]  # ,"server2"]
server_addr = {"server1":"10.1.39.116:5000"}#,"server2":"10.42.0.37:5000"}
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


if __name__ == "__main__":
    app.run(debug=True, port=8080, host="10.1.39.116")
