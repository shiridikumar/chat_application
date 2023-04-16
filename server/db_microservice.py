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


PORT=8080
app=Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app,support_credentials=True)


conn = MongoClient("localhost",27017)
db = conn.users
collection = db.server_mapping


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


@app.route("/server_map",methods=["POST"])
@cross_origin(supports_credentials=True,origin='*')
def server_map():
    data=request.data
    # print(data)
    data=json.loads(data)
    print(data)
    if(data["msg"]!="CONNECT_MSG"):
        user=collection.find_one({"_id":ObjectId(data["_id"])})
        user["_id"]=str(user["_id"])
        return user
    return {1:1}
    
if __name__=="__main__":
    app.run(debug=True,port=8080)