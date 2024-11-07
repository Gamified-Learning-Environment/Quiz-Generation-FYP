from flask import Flask
import pymongo # import pymongo
from app import app
from config import MONGODB_URI


client = pymongo.MongoClient(MONGODB_URI) # create a client

userdb = client.get_database('userdatabase') # get the database
quizdb = client.get_database('Quizdatabase') # get the database
notesdb = client.get_database('notesdatabase') # get the database
user_collection = userdb.usercollection # get the user collection
quiz_collection = quizdb.quizcollection # get the quiz collection
notes_collection = notesdb.notescollection # get the notes collection

# Test connection
client.server_info()