"""User service layer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import RegisterRequest, UserUpdate
from app.utils.errors import bad_request, phone_already_registered, unauthorized
from app.utils.security import hash_password, verify_password


class UserService:
    """Business logic for user accounts."""

    @staticmethod
    async def register(payload: RegisterRequest, session: AsyncSession) -> User:
        """Register a new user."""

        try:
            result = await session.execute(select(User).where(User.phone == payload.phone))
            existing_user = result.scalar_one_or_none()
            if existing_user is not None:
                raise phone_already_registered("该手机号已注册")

            user = User(
                phone=payload.phone,
                password=hash_password(payload.password),
                nickname=payload.nickname,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def authenticate(phone: str, password: str, session: AsyncSession) -> User:
        """Authenticate a user by phone and password."""

        result = await session.execute(select(User).where(User.phone == phone))
        user = result.scalar_one_or_none()
        if user is None or not verify_password(password, user.password):
            raise unauthorized("手机号或密码错误")
        return user

    @staticmethod
    async def update_profile(user: User, payload: UserUpdate, session: AsyncSession) -> User:
        """Update user profile information."""

        try:
            if payload.nickname is not None:
                user.nickname = payload.nickname
            await session.commit()
            await session.refresh(user)
            return user
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def reset_password(
        user: User,
        old_password: str,
        new_password: str,
        session: AsyncSession,
    ) -> User:
        """Reset user password after verifying old password."""

        if not verify_password(old_password, user.password):
            raise bad_request("原密码错误")
        try:
            user.password = hash_password(new_password)
            await session.commit()
            await session.refresh(user)
            return user
        except Exception:
            await session.rollback()
            raise
