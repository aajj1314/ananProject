"""Electronic fence service layer."""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.fence import ElectronicFence
from app.schemas.fence import FenceAlert, FenceCreate, FenceEvaluation, FenceUpdate
from app.utils.cache import cache_delete
from app.utils.errors import fence_not_found


class FenceService:
    """Business logic for electronic fence configuration and evaluation."""

    @staticmethod
    def _cache_key(device_id: str) -> str:
        return f"fences:{device_id}"

    @staticmethod
    def _distance_meters(
        latitude_a: float,
        longitude_a: float,
        latitude_b: float,
        longitude_b: float,
    ) -> float:
        """Calculate point distance in meters using the haversine formula."""

        earth_radius = 6371000
        latitude_delta = radians(latitude_b - latitude_a)
        longitude_delta = radians(longitude_b - longitude_a)
        origin = radians(latitude_a)
        target = radians(latitude_b)
        value = (
            sin(latitude_delta / 2) ** 2
            + cos(origin) * cos(target) * sin(longitude_delta / 2) ** 2
        )
        return 2 * earth_radius * asin(sqrt(value))

    @staticmethod
    async def list_fences(device: Device, session: AsyncSession) -> list[ElectronicFence]:
        """Return all fences attached to a device."""

        result = await session.execute(
            select(ElectronicFence)
            .where(ElectronicFence.device_id == device.device_id)
            .order_by(ElectronicFence.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def create_fence(
        device: Device,
        payload: FenceCreate,
        session: AsyncSession,
    ) -> ElectronicFence:
        """Create a new fence for a device."""

        try:
            fence = ElectronicFence(
                device_id=device.device_id,
                user_id=device.user_id,
                name=payload.name,
                center_latitude=payload.center_latitude,
                center_longitude=payload.center_longitude,
                radius_meters=payload.radius_meters,
                is_active=payload.is_active,
            )
            session.add(fence)
            await session.commit()
            await session.refresh(fence)
            await cache_delete(FenceService._cache_key(device.device_id))
            return fence
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def get_fence(device: Device, fence_id: int, session: AsyncSession) -> ElectronicFence:
        """Load a device fence by id."""

        result = await session.execute(
            select(ElectronicFence).where(
                ElectronicFence.id == fence_id,
                ElectronicFence.device_id == device.device_id,
            )
        )
        fence = result.scalar_one_or_none()
        if fence is None:
            raise fence_not_found("围栏不存在")
        return fence

    @staticmethod
    async def update_fence(
        fence: ElectronicFence,
        payload: FenceUpdate,
        session: AsyncSession,
    ) -> ElectronicFence:
        """Update fence fields - supports partial updates."""

        try:
            if payload.name is not None:
                fence.name = payload.name
            if payload.center_latitude is not None:
                fence.center_latitude = payload.center_latitude
            if payload.center_longitude is not None:
                fence.center_longitude = payload.center_longitude
            if payload.radius_meters is not None:
                fence.radius_meters = payload.radius_meters
            if payload.is_active is not None:
                fence.is_active = payload.is_active
                if not fence.is_active:
                    fence.last_status = "unknown"
                    fence.last_transition_at = None
            await session.commit()
            await session.refresh(fence)
            await cache_delete(FenceService._cache_key(fence.device_id))
            return fence
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def delete_fence(fence: ElectronicFence, session: AsyncSession) -> None:
        """Delete a device fence."""

        device_id = fence.device_id
        try:
            await session.delete(fence)
            await session.commit()
            await cache_delete(FenceService._cache_key(device_id))
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def evaluate_device_fences(
        device: Device,
        latitude: float,
        longitude: float,
        timestamp,
        session: AsyncSession,
    ) -> tuple[list[FenceEvaluation], list[FenceAlert]]:
        """Evaluate active fences and return state transitions and alerts."""

        result = await session.execute(
            select(ElectronicFence)
            .where(
                ElectronicFence.device_id == device.device_id,
                ElectronicFence.is_active.is_(True),
            )
            .order_by(ElectronicFence.id.asc())
        )
        fences = list(result.scalars().all())

        evaluations: list[FenceEvaluation] = []
        alerts: list[FenceAlert] = []
        for fence in fences:
            distance = FenceService._distance_meters(
                fence.center_latitude,
                fence.center_longitude,
                latitude,
                longitude,
            )
            status = "inside" if distance <= fence.radius_meters else "outside"
            transitioned = fence.last_status not in {"unknown", status}
            if fence.last_status != status:
                fence.last_status = status
                fence.last_transition_at = timestamp
            evaluations.append(
                FenceEvaluation(
                    fence_id=fence.id,
                    fence_name=fence.name,
                    distance_meters=round(distance, 2),
                    status=status,
                    transitioned=transitioned,
                )
            )
            if transitioned and status == "outside":
                alerts.append(
                    FenceAlert(
                        fence_id=fence.id,
                        fence_name=fence.name,
                        distance_meters=round(distance, 2),
                        message=(
                            f"设备 {device.device_id} 已离开电子围栏“{fence.name}”，"
                            f"当前距离中心点 {round(distance, 2)} 米"
                        ),
                    )
                )

        return evaluations, alerts
