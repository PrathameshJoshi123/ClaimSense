import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/policy_intelligence")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
