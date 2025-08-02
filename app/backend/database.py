from pymongo import MongoClient
from datetime import datetime
import os
from bson.objectid import ObjectId

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
if not MONGO_URI:
    raise ValueError("mongo uri not set")
client = MongoClient(MONGO_URI)

db = client["docAI"]
collection = db["documents"]

def insert_document(payload):
    payload["created_at"] = datetime.utcnow()
    result = collection.insert_one(payload)
    return str(result.inserted_id)

def get_document(doc_id):
    return collection.find_one({"_id": ObjectId(doc_id)})

def get_all_documents():
    return list(collection.find())
