"""Location service layer."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.location import LocationRecord
from app.models.user import User
from app.schemas.location import DeviceTelemetryIn, HistorySummary
from app.services.alarm_service import AlarmService
from app.services.fence_service import FenceService
from app.utils.cache import cache_delete, cache_get, cache_set
from app.utils.errors import not_found


class LocationService:
    """Business logic for telemetry ingestion and querying."""

    @staticmethod
    async def ingest_telemetry(payload: DeviceTelemetryIn, session: AsyncSession) -> LocationRecord:
        """Store telemetry and update the latest device snapshot."""

        try:
            result = await session.execute(select(Device).where(Device.device_id == payload.device_id))
            device = result.scalar_one_or_none()
            if device is None:
                raise not_found("Device does not exist")

            final_alarm_type = AlarmService.detect_alarm_type(payload.alarm_type, payload.battery)
            fence_events, fence_alerts = await FenceService.evaluate_device_fences(
                device=device,
                latitude=payload.latitude,
                longitude=payload.longitude,
                timestamp=payload.timestamp,
                session=session,
            )
            if fence_alerts:
                final_alarm_type = 6
            record = LocationRecord(
                device_id=payload.device_id,
                user_id=device.user_id,
                latitude=payload.latitude,
                longitude=payload.longitude,
                altitude=payload.altitude,
                speed=payload.speed,
                battery=payload.battery,
                alarm_type=final_alarm_type,
                fence_events=[event.model_dump() for event in fence_events] if fence_events else None,
                timestamp=payload.timestamp,
            )
            device.battery = payload.battery
            device.last_latitude = payload.latitude
            device.last_longitude = payload.longitude
            device.last_updated = payload.timestamp
            session.add(record)
            if fence_alerts:
                first_alert = fence_alerts[0]
                await AlarmService.create_alarm_if_needed(
                    device=device,
                    alarm_type=6,
                    battery=payload.battery,
                    timestamp=payload.timestamp,
                    session=session,
                    message=first_alert.message,
                    notification_title=f"电子围栏越界：{first_alert.fence_name}",
                    notification_content=first_alert.message,
                )
            else:
                await AlarmService.create_alarm_if_needed(
                    device=device,
                    alarm_type=final_alarm_type,
                    battery=payload.battery,
                    timestamp=payload.timestamp,
                    session=session,
                )
            await session.commit()
            await session.refresh(record)
            await cache_set(
                f"location:latest:{payload.device_id}",
                {
                    "device_id": record.device_id,
                    "timestamp": record.timestamp,
                    "latitude": record.latitude,
                    "longitude": record.longitude,
                    "altitude": record.altitude,
                    "speed": record.speed,
                    "battery": record.battery,
                    "alarm_type": record.alarm_type,
                    "fence_events": record.fence_events,
                },
            )
            await cache_delete(f"devices:user:{device.user_id}")
            return record
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def get_latest_location(device: Device, session: AsyncSession) -> LocationRecord:
        """Get the latest location record for a device."""

        cached_record = await cache_get(f"location:latest:{device.device_id}")
        if cached_record is not None:
            return LocationRecord(**cached_record)

        result = await session.execute(
            select(LocationRecord)
            .where(LocationRecord.device_id == device.device_id)
            .order_by(LocationRecord.timestamp.desc())
            .limit(1)
        )
        record = result.scalar_one_or_none()
        if record is None:
            raise not_found("Location record does not exist")
        await cache_set(
            f"location:latest:{device.device_id}",
            {
                "device_id": record.device_id,
                "timestamp": record.timestamp,
                "latitude": record.latitude,
                "longitude": record.longitude,
                "altitude": record.altitude,
                "speed": record.speed,
                "battery": record.battery,
                "alarm_type": record.alarm_type,
                "fence_events": record.fence_events,
            },
        )
        return record

    @staticmethod
    async def get_history(
        device: Device,
        start_time: datetime,
        end_time: datetime,
        user: User,
        session: AsyncSession,
    ) -> list[LocationRecord]:
        """Get the device location history for a time range."""

        if user.role != "admin" and device.user_id != user.id:
            raise not_found("Device does not exist")
        result = await session.execute(
            select(LocationRecord)
            .where(
                LocationRecord.device_id == device.device_id,
                LocationRecord.timestamp >= start_time,
                LocationRecord.timestamp <= end_time,
            )
            .order_by(LocationRecord.timestamp.asc())
            .limit(5000)
        )
        return list(result.scalars().all())

    @staticmethod
    def build_history_summary(device: Device, records: list[LocationRecord]) -> HistorySummary:
        """Build a compact summary from history records."""

        if not records:
            raise not_found("Location history does not exist")
        latest_record = records[-1]
        alarms_detected = len([record for record in records if record.alarm_type != 0])
        last_alarm_record = next((record for record in reversed(records) if record.alarm_type != 0), None)
        return HistorySummary(
            device_id=device.device_id,
            total_points=len(records),
            start_time=records[0].timestamp,
            end_time=records[-1].timestamp,
            latest_battery=latest_record.battery,
            alarms_detected=alarms_detected,
            last_alarm_type=last_alarm_record.alarm_type if last_alarm_record else None,
        )
