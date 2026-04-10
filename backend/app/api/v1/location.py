"""Location endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.location import DeviceTelemetryIn, LocationRead
from app.services.device_service import DeviceService
from app.services.location_service import LocationService
from app.utils.database import get_db_session
from app.utils.response import success_response
from app.utils.security import get_current_user


router = APIRouter(prefix="/location", tags=["location"])


@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_location(
    payload: DeviceTelemetryIn,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Receive telemetry from a device."""

    record = await LocationService.ingest_telemetry(payload, session)
    return success_response(LocationRead.model_validate(record).model_dump(), message="定位数据已接收")


@router.get("/{device_id}")
async def get_latest_location(
    device_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get the latest location for a device."""

    device = await DeviceService.get_owned_device(device_id, current_user, session)
    record = await LocationService.get_latest_location(device, session)
    return success_response(LocationRead.model_validate(record).model_dump())


@router.get("/history/{device_id}")
async def get_location_history(
    device_id: str,
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get location history for a device and time range."""

    device = await DeviceService.get_owned_device(device_id, current_user, session)
    records = await LocationService.get_history(device, start_time, end_time, current_user, session)
    return success_response([LocationRead.model_validate(record).model_dump() for record in records])


@router.get("/summary/{device_id}")
async def get_location_history_summary(
    device_id: str,
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get a compact history summary for a device and time range."""

    device = await DeviceService.get_owned_device(device_id, current_user, session)
    records = await LocationService.get_history(device, start_time, end_time, current_user, session)
    summary = LocationService.build_history_summary(device, records)
    return success_response(summary.model_dump())
