from pymongo import MongoClient

def db_connect():
    global client
    client = MongoClient("mongodb://localhost:27017/")
    return client["rag_gpt"]
