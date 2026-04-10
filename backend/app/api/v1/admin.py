"""Admin-only endpoints for platform management."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alarm import AlarmRecord, NotificationRecord
from app.models.device import Device
from app.models.user import User
from app.schemas.auth import UserProfile
from app.utils.database import get_db_session
from app.utils.errors import not_found
from app.utils.metrics import get_metrics_registry
from app.utils.response import success_response
from app.utils.security import UserRole, get_admin_user


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
async def list_users(
    _current_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> dict:
    """List all users (admin only)."""

    result = await session.execute(
        select(User).order_by(User.id.desc()).offset(offset).limit(limit)
    )
    users = result.scalars().all()

    count_result = await session.execute(select(func.count(User.id)))
    total = count_result.scalar_one()

    return success_response(
        {
            "items": [
                UserProfile(
                    id=u.id,
                    phone=u.phone,
                    nickname=u.nickname,
                    role=u.role or "user",
                    created_at=u.created_at,
                ).model_dump()
                for u in users
            ],
            "total": total,
            "offset": offset,
            "limit": limit,
        }
    )


@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    _current_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict:
    """Get a specific user (admin only)."""

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise not_found("User not found")

    return success_response(
        UserProfile(
            id=user.id,
            phone=user.phone,
            nickname=user.nickname,
            role=user.role or "user",
            created_at=user.created_at,
        ).model_dump()
    )


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: UserRole,
    _current_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict:
    """Update a user's role (admin only)."""

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise not_found("User not found")

    user.role = role.value
    await session.commit()
    await session.refresh(user)

    return success_response(
        UserProfile(
            id=user.id,
            phone=user.phone,
            nickname=user.nickname,
            role=user.role,
            created_at=user.created_at,
        ).model_dump(),
        message="User role updated",
    )


@router.get("/devices")
async def list_all_devices(
    _current_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> dict:
    """List all devices across all users (admin only)."""

    result = await session.execute(
        select(Device).order_by(Device.device_id.desc()).offset(offset).limit(limit)
    )
    devices = result.scalars().all()

    count_result = await session.execute(select(func.count(Device.device_id)))
    total = count_result.scalar_one()

    return success_response(
        {
            "items": [
                {
                    "device_id": d.device_id,
                    "user_id": d.user_id,
                    "device_name": d.device_name,
                    "battery": d.battery,
                    "last_latitude": d.last_latitude,
                    "last_longitude": d.last_longitude,
                    "last_updated": d.last_updated,
                }
                for d in devices
            ],
            "total": total,
            "offset": offset,
            "limit": limit,
        }
    )


@router.get("/alarms")
async def list_all_alarms(
    _current_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> dict:
    """List all alarms across all devices (admin only)."""

    result = await session.execute(
        select(AlarmRecord).order_by(AlarmRecord.timestamp.desc()).offset(offset).limit(limit)
    )
    alarms = result.scalars().all()

    count_result = await session.execute(select(func.count(AlarmRecord.id)))
    total = count_result.scalar_one()

    return success_response(
        {
            "items": [
                {
                    "id": a.id,
                    "device_id": a.device_id,
                    "user_id": a.user_id,
                    "alarm_type": a.alarm_type,
                    "battery": a.battery,
                    "message": a.message,
                    "timestamp": a.timestamp,
                }
                for a in alarms
            ],
            "total": total,
            "offset": offset,
            "limit": limit,
        }
    )


@router.get("/notifications")
async def list_all_notifications(
    _current_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> dict:
    """List all notifications across all users (admin only)."""

    result = await session.execute(
        select(NotificationRecord)
        .order_by(NotificationRecord.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    notifications = result.scalars().all()

    count_result = await session.execute(select(func.count(NotificationRecord.id)))
    total = count_result.scalar_one()

    return success_response(
        {
            "items": [
                {
                    "id": n.id,
                    "device_id": n.device_id,
                    "user_id": n.user_id,
                    "channel": n.channel,
                    "title": n.title,
                    "content": n.content,
                    "status": n.status,
                    "created_at": n.created_at,
                }
                for n in notifications
            ],
            "total": total,
            "offset": offset,
            "limit": limit,
        }
    )


@router.get("/stats")
async def get_platform_stats(
    _current_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict:
    """Get high-level platform statistics (admin only)."""

    # User count
    user_count = (await session.execute(select(func.count(User.id)))).scalar_one()

    # Device count
    device_count = (await session.execute(select(func.count(Device.device_id)))).scalar_one()

    # Alarm counts
    alarm_count = (await session.execute(select(func.count(AlarmRecord.id)))).scalar_one()

    # Notification counts
    notif_count = (
        await session.execute(select(func.count(NotificationRecord.id)))
    ).scalar_one()

    # Metrics
    registry = get_metrics_registry()
    metrics = registry.get_all_summaries(window_seconds=3600)

    return success_response(
        {
            "users": {"total": user_count},
            "devices": {"total": device_count},
            "alarms": {"total": alarm_count},
            "notifications": {"total": notif_count},
            "metrics": metrics,
        }
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    """Delete a user (admin only, cannot delete self)."""

    if user_id == current_user.id:
        from app.utils.errors import bad_request

        raise bad_request("Cannot delete your own account")

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise not_found("User not found")

    await session.delete(user)
    await session.commit()
