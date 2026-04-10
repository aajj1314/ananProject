"""Electronic fence endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.fence import FenceCreate, FenceRead, FenceUpdate
from app.services.device_service import DeviceService
from app.services.fence_service import FenceService
from app.utils.database import get_db_session
from app.utils.response import success_response
from app.utils.security import get_current_user


router = APIRouter(prefix="/fence", tags=["fence"])


@router.get("/{device_id}")
async def list_fences(
    device_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """List fences for a device."""

    device = await DeviceService.get_owned_device(device_id, current_user, session)
    fences = await FenceService.list_fences(device, session)
    return success_response([FenceRead.model_validate(fence).model_dump() for fence in fences])


@router.post("/{device_id}", status_code=status.HTTP_201_CREATED)
async def create_fence(
    device_id: str,
    payload: FenceCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Create a fence for a device."""

    device = await DeviceService.get_owned_device(device_id, current_user, session)
    fence = await FenceService.create_fence(device, payload, session)
    return success_response(FenceRead.model_validate(fence).model_dump(), message="电子围栏创建成功")


@router.put("/{device_id}/{fence_id}")
async def update_fence(
    device_id: str,
    fence_id: int,
    payload: FenceUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update a fence."""

    device = await DeviceService.get_owned_device(device_id, current_user, session)
    fence = await FenceService.get_fence(device, fence_id, session)
    updated_fence = await FenceService.update_fence(fence, payload, session)
    return success_response(FenceRead.model_validate(updated_fence).model_dump(), message="电子围栏更新成功")


@router.delete("/{device_id}/{fence_id}")
async def delete_fence(
    device_id: str,
    fence_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Delete a fence."""

    device = await DeviceService.get_owned_device(device_id, current_user, session)
    fence = await FenceService.get_fence(device, fence_id, session)
    await FenceService.delete_fence(fence, session)
    return success_response({"fence_id": fence_id}, message="电子围栏删除成功")
