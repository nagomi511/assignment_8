from pymongo import MongoClient
from django.conf import settings

def get_db_connection():
    """Establish connection to MongoDB"""
    try:
        # Without authentication
        client = MongoClient(
            host=settings.MONGODB_HOST,
            port=settings.MONGODB_PORT,
            serverSelectionTimeoutMS=5000
        )
        
     
        db = client[settings.MONGODB_DB]
        # Test connection
        client.server_info()
        return db
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return None
