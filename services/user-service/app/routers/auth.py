from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.user import UserResponse
from app.security.dependencies import get_current_user
from app.security.token import create_access_token
from app.services.user_service import authenticate_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(
        email=form_data.username,
        password=form_data.password,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(str(user["_id"]), user["role"])
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user=Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        **current_user,
    }
