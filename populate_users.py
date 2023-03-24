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
maps=[1,1,2,2]
ind=0
for i in users:
    collection.insert_one({"name":i,"server":maps[ind]})
    ind+=1
