from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError

from app.config import DATABASE_NAME, MONGODB_URL

mongo_client = None
database = None
meetings_collection = None


def connect_database():
    global mongo_client, database, meetings_collection

    client = MongoClient(
        MONGODB_URL,
        serverSelectionTimeoutMS=5000,
        tz_aware=True,
    )
    try:
        client.admin.command("ping")
        db = client[DATABASE_NAME]
        collection = db["meetings"]
        collection.create_index(
            [("organizer_id", ASCENDING), ("start_time", ASCENDING)]
        )
    except PyMongoError:
        client.close()
        raise

    mongo_client = client
    database = db
    meetings_collection = collection


def get_meetings_collection():
    if meetings_collection is None:
        raise RuntimeError("Meeting database is not connected")
    return meetings_collection


def check_database_connection():
    if mongo_client is None:
        return False

    try:
        mongo_client.admin.command("ping")
    except PyMongoError:
        return False
    return True


def close_database():
    global mongo_client, database, meetings_collection

    if mongo_client is not None:
        mongo_client.close()

    mongo_client = None
    database = None
    meetings_collection = None
