from flask import Flask
import pymongo # import pymongo
from app import app
from config import MONGODB_URI


client = pymongo.MongoClient(MONGODB_URI) # create a client
db = client.get_database('userdatabase') # get the database
user_collection = db.usercollection # get the collection

# Test connection
client.server_info()