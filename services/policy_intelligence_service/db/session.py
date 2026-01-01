from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient
from services.policy_intelligence_service.core.config import MONGO_URI

print(f"Connecting to MongoDB at {MONGO_URI}")

client = MongoClient(MONGO_URI)
db = client.policy_intelligence
user_db = client.user_db

def get_db():
    return db

def get_users_collection():
    return user_db.users
