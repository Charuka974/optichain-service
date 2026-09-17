import os
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "optichain_db")

client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
db = client[MONGODB_DB_NAME]

def get_db():
    """
    Dependency helper to retrieve database instance for route handlers.
    """
    yield db

def init_db():
    """
    Initializes database indexes and verifies connectivity.
    """
    try:
        # Ping the server to check connectivity
        client.admin.command('ping')
        print(f"Successfully connected to MongoDB Atlas / Database: {MONGODB_DB_NAME}")
    except Exception as e:
        print(f"Warning: Could not connect to MongoDB at {MONGODB_URL}: {e}")

    # Ensure unique index on email for users collection
    db["users"].create_index([("email", ASCENDING)], unique=True)