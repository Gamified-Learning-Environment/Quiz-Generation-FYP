import pymongo # import pymongo for database connection
from gridfs import GridFS # import GridFS for file storage
import os

# Try to import from config, fall back to environment variable if config not available
try:
    from config import MONGODB_URI
except ImportError:
    # When deployed, get from environment variable
    MONGODB_URI = os.environ.get('MONGODB_URI')
    
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI environment variable not set")

# Create database connections
client = pymongo.MongoClient(MONGODB_URI) # create a client
quizdb = client.get_database('Quizdatabase') # get the database
userdb = client.get_database('userdatabase') # get the database
notesdb = client.get_database('notesdatabase') # get the database

user_collection = userdb.usercollection # get the user collection
quiz_collection = quizdb.quizcollection # get the quiz collection
notes_collection = notesdb.notescollection # get the notes collection

# Initialize GridFS for file storage
fs = GridFS(quizdb)

# index creation for image URLs and metadata, to speed up queries
quizdb.quizcollection.create_index([
    ('questions.imageUrl', pymongo.ASCENDING),
    ('questions.imageMetadata.uploadDate', pymongo.ASCENDING)
])

# collection creation for tracking image metadata
image_collection = quizdb.imagecollection
image_collection.create_index([
    ('url', pymongo.ASCENDING),
    ('uploadDate', pymongo.ASCENDING)
])

# Test connection
client.server_info()