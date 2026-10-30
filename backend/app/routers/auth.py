from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.errors import ApiError, ErrorCode
from app.models import User
from app.schemas import ErrorEnvelope, LoginRequest, TokenResponse
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=200,
    responses={
        401: {"model": ErrorEnvelope, "description": "Invalid credentials"},
        422: {"model": ErrorEnvelope, "description": "Validation error"},
    },
    openapi_extra={"security": []},
)
async def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise ApiError(ErrorCode.INVALID_CREDENTIALS, "Invalid email or password", 401)

    expires_in = settings.access_token_expire_minutes * 60
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        token_type="bearer",
        expires_in=expires_in,
    )
