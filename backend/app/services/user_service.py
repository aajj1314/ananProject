"""User service layer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.utils.errors import conflict, unauthorized
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
                raise conflict("Phone number is already registered")

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
            raise unauthorized("Invalid phone number or password")
        return user
