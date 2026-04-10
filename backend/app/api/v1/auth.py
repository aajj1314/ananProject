"""Authentication endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import LoginRequest, RegisterRequest, TokenPayload
from app.services.user_service import UserService
from app.utils.database import get_db_session
from app.utils.response import success_response
from app.utils.security import create_access_token


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Register a user and return a token."""

    user = await UserService.register(payload, session)
    token = create_access_token(str(user.id))
    return success_response(TokenPayload(access_token=token).model_dump())


@router.post("/login")
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Authenticate and return a JWT token."""

    user = await UserService.authenticate(payload.phone, payload.password, session)
    token = create_access_token(str(user.id))
    return success_response(TokenPayload(access_token=token).model_dump())
