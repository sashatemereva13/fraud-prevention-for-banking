from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = MongoClient(MONGO_URI)

db = client["fraud_detection"]

transactions_collection = db["transactions"]
users_collection = db["users"]
alerts_collection = db["alerts"]

# INDEXES 

transactions_collection.create_index("sender.user_id")
transactions_collection.create_index("timestamp")
transactions_collection.create_index("receiver.user_id")