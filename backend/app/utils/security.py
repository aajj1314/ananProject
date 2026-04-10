"""Authentication and password security helpers."""

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import User
from app.utils.database import get_db_session
from app.utils.errors import forbidden, unauthorized


class UserRole(str, Enum):
    """Valid user roles."""

    USER = "user"
    ADMIN = "admin"


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
settings = get_settings()


def hash_password(password: str) -> str:
    """Hash the provided password."""

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash."""

    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, role: str = UserRole.USER) -> str:
    """Create a signed JWT access token with role claim."""

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "role": role, "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    """Resolve the authenticated user from a JWT token."""

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        subject = payload.get("sub")
        if not subject:
            raise unauthorized("Missing token subject")
        result = await session.execute(select(User).where(User.id == int(subject)))
        user = result.scalar_one_or_none()
        if user is None:
            raise unauthorized("User not found")
        return user
    except JWTError as exc:
        raise unauthorized(str(exc)) from exc
    except ValueError as exc:
        raise unauthorized("Invalid token subject") from exc


def require_role(*required_roles: UserRole):
    """Dependency factory to require specific roles for an endpoint."""

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        """Verify the user has at least one of the required roles."""

        user_role = current_user.role
        if not user_role:
            user_role = UserRole.USER

        if user_role not in required_roles and UserRole.ADMIN not in required_roles:
            if UserRole.ADMIN == user_role:
                return current_user
            raise forbidden(f"Requires one of roles: {', '.join(required_roles)}")

        return current_user

    return role_checker


# Convenience dependencies
async def get_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Require admin role."""

    if current_user.role != UserRole.ADMIN:
        raise forbidden("Admin access required")
    return current_user


async def get_any_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Accept any authenticated user (user or admin)."""

    return current_user
