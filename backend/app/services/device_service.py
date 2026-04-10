"""Device service layer."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.fence import ElectronicFence
from app.models.user import User
from app.schemas.device import DeviceCreate, DeviceUpdate
from app.utils.cache import cache_delete, cache_get, cache_set
from app.utils.errors import conflict, not_found, unauthorized


class DeviceService:
    """Business logic for device management."""

    @staticmethod
    async def list_devices(user: User, session: AsyncSession) -> list[Device]:
        """List devices visible to the user."""

        cache_key = f"devices:{user.role}:{user.id}"
        cached_devices = await cache_get(cache_key)
        if cached_devices is not None:
            return [Device(**item) for item in cached_devices]

        statement = select(Device)
        if user.role != "admin":
            statement = statement.where(Device.user_id == user.id)
        result = await session.execute(statement.order_by(Device.last_updated.desc().nullslast()))
        devices = list(result.scalars().all())
        await cache_set(
            cache_key,
            [
                {
                    "device_id": device.device_id,
                    "user_id": device.user_id,
                    "device_name": device.device_name,
                    "battery": device.battery,
                    "last_latitude": device.last_latitude,
                    "last_longitude": device.last_longitude,
                    "last_updated": device.last_updated,
                }
                for device in devices
            ],
        )
        return devices

    @staticmethod
    async def bind_device(payload: DeviceCreate, user: User, session: AsyncSession) -> Device:
        """Bind a new device to the current user."""

        try:
            result = await session.execute(select(Device).where(Device.device_id == payload.device_id))
            existing_device = result.scalar_one_or_none()
            if existing_device is not None:
                raise conflict("Device is already bound")

            device = Device(
                device_id=payload.device_id,
                user_id=user.id,
                device_name=payload.device_name,
            )
            session.add(device)
            await session.commit()
            await session.refresh(device)
            await cache_delete(f"devices:{user.role}:{user.id}")
            return device
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def update_device(
        device: Device,
        payload: DeviceUpdate,
        user: User,
        session: AsyncSession,
    ) -> Device:
        """Update user-editable device metadata."""

        try:
            device.device_name = payload.device_name
            await session.commit()
            await session.refresh(device)
            await cache_delete(f"devices:{user.role}:{user.id}")
            return device
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def unbind_device(device: Device, user: User, session: AsyncSession) -> None:
        """Unbind a device from the current user."""

        try:
            await session.execute(
                delete(ElectronicFence).where(ElectronicFence.device_id == device.device_id)
            )
            await session.delete(device)
            await session.commit()
            await cache_delete(f"devices:{user.role}:{user.id}")
            await cache_delete(f"location:latest:{device.device_id}")
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def get_owned_device(device_id: str, user: User, session: AsyncSession) -> Device:
        """Get a device and enforce ownership."""

        result = await session.execute(select(Device).where(Device.device_id == device_id))
        device = result.scalar_one_or_none()
        if device is None:
            raise not_found("Device does not exist")
        if user.role != "admin" and device.user_id != user.id:
            raise unauthorized("You do not have access to this device")
        return device
