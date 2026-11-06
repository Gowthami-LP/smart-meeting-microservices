from fastapi import APIRouter, HTTPException, status

from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import (
    DuplicateUserError,
    create_user,
    get_all_users,
    get_user_by_id,
)

router = APIRouter(prefix="/users", tags=["Users"])


def _user_response(user):
    user["id"] = str(user.pop("_id"))
    return user


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user_data: UserCreate):
    try:
        user = create_user(user_data)
    except DuplicateUserError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    return _user_response(user)


@router.get("")
def get_users():
    users = [_user_response(user) for user in get_all_users()]
    return {
        "message": "Get users endpoint is working",
        "users": users,
    }


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return _user_response(user)
