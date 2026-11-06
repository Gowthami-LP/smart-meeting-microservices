from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=150)
    department: str | None = None


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    department: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
