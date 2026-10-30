from fastapi import APIRouter, Depends

from app.deps import get_current_user
from app.models import User
from app.schemas import ErrorEnvelope, UserResponse

router = APIRouter(tags=["me"])


@router.get(
    "/me",
    response_model=UserResponse,
    responses={401: {"model": ErrorEnvelope, "description": "Missing or invalid token"}},
)
async def read_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
