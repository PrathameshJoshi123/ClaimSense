from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")


client = MongoClient(MONGO_URI)
policy_db = client.policy_intelligence

def get_policy_db():
    return policy_db

def get_policies_collection():
    return policy_db.policies
