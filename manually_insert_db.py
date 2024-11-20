from pymongo import MongoClient
import os

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB_NAME = "Development"
mongo_client = MongoClient(MONGO_HOST, MONGO_PORT)
db = mongo_client[MONGO_DB_NAME]

def insert_assistant(name, system_prompt, process_prompt, db = db):
    configs_collection = db.agents
    assistant_dct = {'name': name,
                     'system_prompt':system_prompt, 
                     'process_prompt': process_prompt}
    result = configs_collection.insert_one(assistant_dct)
    return result.inserted_id