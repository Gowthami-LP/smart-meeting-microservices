from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError

from app.schemas.meeting import MeetingCreate, MeetingResponse, MeetingUpdate
from app.security.dependencies import get_current_user
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
def create_new_meeting(
    meeting_data: MeetingCreate,
    current_user: dict = Depends(get_current_user),
):
    if meeting_data.organizer_id != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the authenticated user can organize this meeting",
        )
    return _meeting_response(create_meeting(meeting_data))


@router.get("")
def get_meetings(_: dict = Depends(get_current_user)):
    meetings = [_meeting_response(meeting) for meeting in get_all_meetings()]
    return {
        "message": "Meeting list endpoint is working",
        "meetings": meetings,
    }


@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(meeting_id: str, _: dict = Depends(get_current_user)):
    meeting = get_meeting_by_id(meeting_id)
    if meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )
    return _meeting_response(meeting)


@router.patch("/{meeting_id}", response_model=MeetingResponse)
def update_existing_meeting(
    meeting_id: str,
    meeting_data: MeetingUpdate,
    current_user: dict = Depends(get_current_user),
):
    existing = get_meeting_by_id(meeting_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )
    if (
        existing["organizer_id"] != current_user["sub"]
        and current_user.get("role") != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the meeting organizer can update this meeting",
        )
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
def cancel_existing_meeting(
    meeting_id: str,
    current_user: dict = Depends(get_current_user),
):
    existing = get_meeting_by_id(meeting_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )
    if (
        existing["organizer_id"] != current_user["sub"]
        and current_user.get("role") != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the meeting organizer can cancel this meeting",
        )
    meeting = cancel_meeting(meeting_id)
    if meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )
    return _meeting_response(meeting)
