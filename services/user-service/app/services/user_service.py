from datetime import datetime, timezone

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.database import get_users_collection
from app.schemas.user import UserCreate


class DuplicateUserError(Exception):
    pass


def create_user(user_data: UserCreate):
    collection = get_users_collection()
    user_document = {
        "name": user_data.name,
        "email": user_data.email.lower().strip(),
        "department": user_data.department,
        "created_at": datetime.now(timezone.utc),
    }

    try:
        result = collection.insert_one(user_document)
    except DuplicateKeyError as error:
        raise DuplicateUserError("A user with this email already exists") from error

    user_document["_id"] = result.inserted_id
    return user_document


def get_all_users():
    return list(get_users_collection().find().sort("created_at", -1))


def get_user_by_id(user_id: str):
    if not ObjectId.is_valid(user_id):
        return None
    return get_users_collection().find_one({"_id": ObjectId(user_id)})
