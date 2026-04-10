"""Device endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.device import DeviceCreate, DeviceRead, DeviceUpdate
from app.services.device_service import DeviceService
from app.utils.database import get_db_session
from app.utils.response import success_response
from app.utils.security import get_current_user


router = APIRouter(prefix="/device", tags=["device"])


@router.get("")
async def list_devices(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """List devices owned by the current user."""

    devices = await DeviceService.list_devices(current_user, session)
    return success_response([DeviceRead.model_validate(device).model_dump() for device in devices])


@router.post("", status_code=status.HTTP_201_CREATED)
async def bind_device(
    payload: DeviceCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Bind a new device."""

    device = await DeviceService.bind_device(payload, current_user, session)
    return success_response(DeviceRead.model_validate(device).model_dump(), message="设备绑定成功")


@router.put("/{device_id}")
async def update_device(
    device_id: str,
    payload: DeviceUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update a device."""

    device = await DeviceService.get_owned_device(device_id, current_user, session)
    updated_device = await DeviceService.update_device(device, payload, current_user, session)
    return success_response(DeviceRead.model_validate(updated_device).model_dump(), message="设备更新成功")


@router.delete("/{device_id}")
async def unbind_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Unbind a device."""

    device = await DeviceService.get_owned_device(device_id, current_user, session)
    await DeviceService.unbind_device(device, current_user, session)
    return success_response({"device_id": device_id}, message="设备解绑成功")
