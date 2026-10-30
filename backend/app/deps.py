import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import ApiError, ErrorCode
from app.models import User
from app.security import decode_access_token

bearer_scheme = HTTPBearer(
    scheme_name="bearerAuth",
    bearerFormat="JWT",
    auto_error=False,
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or not credentials.credentials:
        raise ApiError(ErrorCode.UNAUTHORIZED, "Missing authorization token", 401)

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise ApiError(ErrorCode.INVALID_TOKEN, "Invalid or expired token", 401)

    try:
        uid = uuid.UUID(user_id)
    except (ValueError, TypeError):
        raise ApiError(ErrorCode.INVALID_TOKEN, "Invalid or expired token", 401)

    user = db.get(User, uid)
    if user is None:
        raise ApiError(ErrorCode.INVALID_TOKEN, "Invalid or expired token", 401)

    return user
