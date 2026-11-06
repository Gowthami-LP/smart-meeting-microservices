from datetime import datetime, timezone

from bson import ObjectId

from app.database import get_meetings_collection
from app.schemas.meeting import MeetingCreate, MeetingUpdate


def create_meeting(meeting_data: MeetingCreate):
    now = datetime.now(timezone.utc)
    meeting_document = {
        **meeting_data.model_dump(),
        "status": "scheduled",
        "created_at": now,
        "updated_at": now,
    }
    result = get_meetings_collection().insert_one(meeting_document)
    meeting_document["_id"] = result.inserted_id
    return meeting_document


def get_all_meetings():
    return list(get_meetings_collection().find().sort("start_time", 1))


def get_meeting_by_id(meeting_id: str):
    if not ObjectId.is_valid(meeting_id):
        return None
    return get_meetings_collection().find_one({"_id": ObjectId(meeting_id)})


def update_meeting(meeting_id: str, meeting_data: MeetingUpdate):
    if not ObjectId.is_valid(meeting_id):
        return None

    collection = get_meetings_collection()
    object_id = ObjectId(meeting_id)
    existing = collection.find_one({"_id": object_id})
    if existing is None:
        return None

    updates = meeting_data.model_dump(exclude_unset=True)
    if not updates:
        return existing

    current = {
        key: existing[key]
        for key in (
            "title",
            "description",
            "organizer_id",
            "participant_ids",
            "start_time",
            "end_time",
        )
    }
    validated = MeetingCreate.model_validate({**current, **updates})
    updates = validated.model_dump()
    updates["updated_at"] = datetime.now(timezone.utc)
    collection.update_one({"_id": object_id}, {"$set": updates})
    return collection.find_one({"_id": object_id})


def cancel_meeting(meeting_id: str):
    if not ObjectId.is_valid(meeting_id):
        return None

    collection = get_meetings_collection()
    object_id = ObjectId(meeting_id)
    cancelled_at = datetime.now(timezone.utc)
    result = collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "status": "cancelled",
                "cancelled_at": cancelled_at,
                "updated_at": cancelled_at,
            }
        },
    )
    if result.matched_count == 0:
        return None
    return collection.find_one({"_id": object_id})
