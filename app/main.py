import os
from fastapi import FastAPI
from pymongo import MongoClient
from database.mongo_connection import MongoConnection

app = FastAPI()

# Connect to MongoDB
mongo_connection = MongoConnection(
    db_name='rainarlert',
    username=os.environ.get("MONGO_USERNAME"),
    password=os.environ.get("MONGO_PASSWORD"),
    host='cp23tt3.sit.kmutt.ac.th',
)
db = mongo_connection.get_database()

# Create rain report every 5 minutes

# Close MongoDB connection when done
mongo_connection.close_connection()

