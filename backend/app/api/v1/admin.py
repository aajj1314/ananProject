"""Admin-only endpoints for platform management."""

import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alarm import AlarmRecord, NotificationRecord
from app.models.device import Device
from app.models.user import User
from app.schemas.auth import UserProfile
from app.schemas.device import DeviceRead
from app.schemas.alarm import AlarmRead, NotificationRead
from app.utils.database import get_db_session
from app.utils.errors import bad_request, user_not_found
from app.utils.metrics import get_metrics_registry
from app.utils.response import success_response
from app.utils.security import UserRole, get_admin_user


router = APIRouter(prefix="/admin", tags=["admin"])


class RoleUpdateRequest(BaseModel):
    """Role update request body."""

    role: UserRole


@router.get("/stats")
async def get_platform_stats(
    _current_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict:
    """Get high-level platform statistics (admin only)."""

    # Execute all COUNT queries in parallel for better performance
    user_count_result, device_count_result, alarm_count_result, notif_count_result = await asyncio.gather(
        session.execute(select(func.count(User.id))),
        session.execute(select(func.count(Device.device_id))),
        session.execute(select(func.count(AlarmRecord.id))),
        session.execute(select(func.count(NotificationRecord.id))),
    )

    user_count = user_count_result.scalar_one()
    device_count = device_count_result.scalar_one()
    alarm_count = alarm_count_result.scalar_one()
    notif_count = notif_count_result.scalar_one()

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
        raise user_not_found("用户不存在")

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
    payload: RoleUpdateRequest,
    _current_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict:
    """Update a user's role (admin only)."""

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise user_not_found("用户不存在")

    user.role = payload.role.value
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
        message="用户角色更新成功",
    )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict:
    """Delete a user (admin only, cannot delete self)."""

    if user_id == current_user.id:
        raise bad_request("不能删除自己的账号")

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise user_not_found("用户不存在")

    await session.delete(user)
    await session.commit()
    return success_response({"user_id": user_id}, message="用户删除成功")


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
            "items": [DeviceRead.model_validate(d).model_dump() for d in devices],
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
            "items": [AlarmRead.model_validate(a).model_dump() for a in alarms],
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
            "items": [NotificationRead.model_validate(n).model_dump() for n in notifications],
            "total": total,
            "offset": offset,
            "limit": limit,
        }
    )
