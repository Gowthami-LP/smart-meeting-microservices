from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import DATABASE_NAME, MONGODB_URL

mongo_client = None
database = None
users_collection = None


def connect_database():
    global mongo_client, database, users_collection

    client = MongoClient(
        MONGODB_URL,
        serverSelectionTimeoutMS=5000,
        tz_aware=True,
    )
    try:
        client.admin.command("ping")
        db = client[DATABASE_NAME]
        collection = db["users"]
        collection.create_index("email", unique=True)
    except PyMongoError:
        client.close()
        raise

    mongo_client = client
    database = db
    users_collection = collection


def get_users_collection():
    if users_collection is None:
        raise RuntimeError("User database is not connected")
    return users_collection


def check_database_connection():
    if mongo_client is None:
        return False

    try:
        mongo_client.admin.command("ping")
    except PyMongoError:
        return False
    return True


def close_database():
    global mongo_client, database, users_collection

    if mongo_client is not None:
        mongo_client.close()

    mongo_client = None
    database = None
    users_collection = None
