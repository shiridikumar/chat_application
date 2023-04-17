import collections
import pymongo
from pymongo import MongoClient

try:
	conn = MongoClient("localhost",27017)
	print("Connected successfully!!!")
except:
	print("Could not connect to MongoDB")

# database
db = conn.users

# Created or Switched to collection names: my_gfg_collection
collection = db.server_mapping
users=["Mukund","Narayna","Kiran","Shiridi"]
maps=[5050,5050,5000,5000]
collection.delete_many({})
ind=0
for i in users:
    collection.insert_one({"name":i,"server":"10.1.39.116:"+str(maps[ind])})
    ind+=1
	

servers=[5000,5050]
server_Collection=db.servers
server_Collection.delete_many({})
for i in servers:
	server_Collection.insert_one({"PORT":i})

