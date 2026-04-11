"""Device service layer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.user import User
from app.schemas.device import DeviceCreate, DeviceUpdate
from app.utils.cache import cache_delete, cache_get, cache_set
from app.utils.errors import conflict, device_not_found, forbidden


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
                raise conflict("设备已绑定")

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
        """Unbind a device from the current user.

        Related fences, locations, alarms and notifications are
        automatically cascade-deleted by the ORM relationship.
        """

        try:
            device_id = device.device_id
            await session.delete(device)
            await session.commit()
            await cache_delete(f"devices:{user.role}:{user.id}")
            await cache_delete(f"location:latest:{device_id}")
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def get_owned_device(device_id: str, user: User, session: AsyncSession) -> Device:
        """Get a device and enforce ownership, with cache for frequent lookups."""

        # Try cache first to reduce DB queries on hot paths (e.g. alarm polling)
        cache_key = f"device:owned:{device_id}:{user.id}"
        cached = await cache_get(cache_key)
        if cached is not None:
            device = Device(**cached)
            if user.role != "admin" and device.user_id != user.id:
                raise forbidden("您没有权限访问此设备")
            return device

        result = await session.execute(select(Device).where(Device.device_id == device_id))
        device = result.scalar_one_or_none()
        if device is None:
            raise device_not_found("设备不存在")
        if user.role != "admin" and device.user_id != user.id:
            raise forbidden("您没有权限访问此设备")

        # Cache the device lookup for a short TTL to reduce repeated queries
        await cache_set(
            cache_key,
            {
                "device_id": device.device_id,
                "user_id": device.user_id,
                "device_name": device.device_name,
                "battery": device.battery,
                "last_latitude": device.last_latitude,
                "last_longitude": device.last_longitude,
                "last_updated": device.last_updated,
            },
            ttl_seconds=30,  # Short TTL since device data changes frequently
        )
        return device
