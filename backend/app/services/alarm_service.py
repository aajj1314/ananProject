"""Alarm service layer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alarm import AlarmRecord, NotificationRecord
from app.models.device import Device
from app.services.notification_service import NotificationService


ALARM_MESSAGES = {
    1: "检测到防拆报警",
    2: "检测到跌倒报警",
    3: "检测到静止报警",
    4: "检测到低电量报警",
    5: "检测到 SOS 报警",
    6: "检测到电子围栏越界报警",
}


class AlarmService:
    """Alarm classification and query logic."""

    @staticmethod
    def detect_alarm_type(explicit_alarm_type: int, battery: int) -> int:
        """Return the final alarm type based on explicit and derived rules."""

        if explicit_alarm_type in {1, 2, 3, 5}:
            return explicit_alarm_type
        if battery < 20:
            return 4
        return 0

    @staticmethod
    async def create_alarm_if_needed(
        device: Device,
        alarm_type: int,
        battery: int,
        timestamp,
        session: AsyncSession,
        *,
        message: str | None = None,
        notification_title: str | None = None,
        notification_content: str | None = None,
    ) -> AlarmRecord | None:
        """Create an alarm record and notification log if needed."""

        if alarm_type == 0:
            return None

        alarm = AlarmRecord(
            device_id=device.device_id,
            user_id=device.user_id,
            alarm_type=alarm_type,
            battery=battery,
            message=message or ALARM_MESSAGES.get(alarm_type, "设备触发未知报警"),
            timestamp=timestamp,
        )
        session.add(alarm)
        await session.flush()
        await NotificationService.create_alarm_notification(
            device_id=device.device_id,
            user_id=device.user_id,
            alarm_type=alarm_type,
            battery=battery,
            session=session,
            title=notification_title,
            content=notification_content,
        )
        return alarm

    @staticmethod
    async def list_alarms(device: Device, session: AsyncSession, limit: int = 20) -> list[AlarmRecord]:
        """Return recent alarms for a device."""

        result = await session.execute(
            select(AlarmRecord)
            .where(AlarmRecord.device_id == device.device_id)
            .order_by(AlarmRecord.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def list_notifications(
        device: Device,
        session: AsyncSession,
        limit: int = 20,
    ) -> list[NotificationRecord]:
        """Return recent notification logs for a device."""

        result = await session.execute(
            select(NotificationRecord)
            .where(NotificationRecord.device_id == device.device_id)
            .order_by(NotificationRecord.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
