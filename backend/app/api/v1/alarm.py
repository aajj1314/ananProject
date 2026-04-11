"""Alarm endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.alarm import AlarmRead, AlarmLatestRead, NotificationRead
from app.services.alarm_service import AlarmService
from app.services.device_service import DeviceService
from app.services.location_service import LocationService
from app.utils.database import get_db_session
from app.utils.response import success_response
from app.utils.security import get_current_user


router = APIRouter(prefix="/alarm", tags=["alarm"])


@router.get("/{device_id}")
async def get_latest_alarm(
    device_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Return the latest alarm state for a device."""

    device = await DeviceService.get_owned_device(device_id, current_user, session)
    record = await LocationService.get_latest_location(device, session)
    return success_response(
        AlarmLatestRead(
            device_id=device.device_id,
            alarm_type=record.alarm_type,
            battery=record.battery,
            timestamp=record.timestamp,
        ).model_dump()
    )


@router.get("/history/{device_id}")
async def list_alarm_history(
    device_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    limit: int = Query(20, ge=1, le=200),
) -> dict:
    """Return recent alarm events for a device."""

    device = await DeviceService.get_owned_device(device_id, current_user, session)
    alarms = await AlarmService.list_alarms(device, session, limit=limit)
    return success_response([AlarmRead.model_validate(alarm).model_dump() for alarm in alarms])


@router.get("/notifications/{device_id}")
async def list_notification_history(
    device_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    limit: int = Query(20, ge=1, le=200),
) -> dict:
    """Return recent notification logs for a device."""

    device = await DeviceService.get_owned_device(device_id, current_user, session)
    notifications = await AlarmService.list_notifications(device, session, limit=limit)
    return success_response(
        [NotificationRead.model_validate(notification).model_dump() for notification in notifications]
    )
