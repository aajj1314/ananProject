"""Authentication endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    PasswordReset,
    RegisterRequest,
    TokenPayload,
    UserProfile,
    UserUpdate,
)
from app.services.user_service import UserService
from app.utils.database import get_db_session
from app.utils.response import success_response
from app.utils.security import create_access_token, get_any_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Register a user and return a token."""

    user = await UserService.register(payload, session)
    token = create_access_token(str(user.id), user.role or "user")
    return success_response(TokenPayload(access_token=token).model_dump())


@router.post("/login")
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Authenticate and return a JWT token."""

    user = await UserService.authenticate(payload.phone, payload.password, session)
    token = create_access_token(str(user.id), user.role or "user")
    return success_response(TokenPayload(access_token=token).model_dump())


@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_any_user),
) -> dict:
    """Get the current user's profile."""

    return success_response(
        UserProfile(
            id=current_user.id,
            phone=current_user.phone,
            nickname=current_user.nickname,
            role=current_user.role or "user",
            created_at=current_user.created_at,
        ).model_dump()
    )


@router.put("/profile")
async def update_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_any_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update the current user's profile."""

    user = await UserService.update_profile(current_user, payload, session)
    return success_response(
        UserProfile(
            id=user.id,
            phone=user.phone,
            nickname=user.nickname,
            role=user.role or "user",
            created_at=user.created_at,
        ).model_dump(),
        message="用户信息更新成功",
    )


@router.put("/password")
async def reset_password(
    payload: PasswordReset,
    current_user: User = Depends(get_any_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Reset the current user's password."""

    await UserService.reset_password(
        current_user,
        payload.old_password,
        payload.new_password,
        session,
    )
    return success_response(None, message="密码修改成功")
