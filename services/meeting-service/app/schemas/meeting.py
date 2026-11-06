from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MeetingCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str | None = None
    organizer_id: str
    participant_ids: list[str] = Field(default_factory=list)
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def validate_meeting_time(self):
        if self.start_time.tzinfo is None or self.end_time.tzinfo is None:
            raise ValueError("Meeting start and end times must include a timezone")
        if self.end_time <= self.start_time:
            raise ValueError("Meeting end time must be after its start time")
        return self


class MeetingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = None
    organizer_id: str | None = None
    participant_ids: list[str] | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None


class MeetingResponse(BaseModel):
    id: str
    title: str
    description: str | None = None
    organizer_id: str
    participant_ids: list[str]
    start_time: datetime
    end_time: datetime
    status: Literal["scheduled", "cancelled"]
    cancelled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
