from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from app.schemas.meeting import MeetingCreate, MeetingResponse, MeetingUpdate
from app.services.meeting_service import (
    cancel_meeting,
    create_meeting,
    get_all_meetings,
    get_meeting_by_id,
    update_meeting,
)

router = APIRouter(prefix="/meetings", tags=["Meetings"])


def _meeting_response(meeting):
    meeting["id"] = str(meeting.pop("_id"))
    return meeting


@router.post(
    "",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_meeting(meeting_data: MeetingCreate):
    return _meeting_response(create_meeting(meeting_data))


@router.get("")
def get_meetings():
    meetings = [_meeting_response(meeting) for meeting in get_all_meetings()]
    return {
        "message": "Meeting list endpoint is working",
        "meetings": meetings,
    }


@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(meeting_id: str):
    meeting = get_meeting_by_id(meeting_id)
    if meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )
    return _meeting_response(meeting)


@router.patch("/{meeting_id}", response_model=MeetingResponse)
def update_existing_meeting(meeting_id: str, meeting_data: MeetingUpdate):
    try:
        meeting = update_meeting(meeting_id, meeting_data)
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.errors(),
        ) from error

    if meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )
    return _meeting_response(meeting)


@router.patch("/{meeting_id}/cancel", response_model=MeetingResponse)
def cancel_existing_meeting(meeting_id: str):
    meeting = cancel_meeting(meeting_id)
    if meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )
    return _meeting_response(meeting)
