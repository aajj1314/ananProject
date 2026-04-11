"""Alarm service layer."""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alarm import AlarmRecord, NotificationRecord
from app.models.device import Device
from app.models.user import User
from app.services.notification_service import NotificationService
from app.utils.errors import device_not_found
from app.utils.notifications import get_notification_router

logger = logging.getLogger(__name__)


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

        alarm_msg = message or ALARM_MESSAGES.get(alarm_type, "设备触发未知报警")
        title = notification_title or f"⚠️ {alarm_msg}"
        content = notification_content or f"设备 {device.device_name} ({device.device_id}) 触发报警：{alarm_msg}，当前电量 {battery}%"

        alarm = AlarmRecord(
            device_id=device.device_id,
            user_id=device.user_id,
            alarm_type=alarm_type,
            battery=battery,
            message=alarm_msg,
            timestamp=timestamp,
        )
        session.add(alarm)
        await session.flush()

        # Create in-app notification first
        await NotificationService.create_alarm_notification(
            device_id=device.device_id,
            user_id=device.user_id,
            alarm_type=alarm_type,
            battery=battery,
            session=session,
            title=title,
            content=content,
        )

        # Try to send via other configured channels
        # Look up the user's phone number for SMS/WeChat delivery
        user_phone = None
        try:
            result = await session.execute(select(User).where(User.id == device.user_id))
            user_obj = result.scalar_one_or_none()
            if user_obj is not None:
                user_phone = user_obj.phone
        except Exception:
            logger.warning(f"Failed to look up user phone for user_id={device.user_id}")

        router = get_notification_router()
        recipient = user_phone or str(device.user_id)

        try:
            results = await router.send_to_all_available(
                recipient=recipient,
                title=title,
                content=content,
                channel_allowlist=None,  # Use configured channels from settings
            )

            # Log notification delivery results
            for channel, (success, status_msg) in results.items():
                if channel != "in_app":
                    channel_notification = NotificationRecord(
                        device_id=device.device_id,
                        user_id=device.user_id,
                        channel=channel,
                        title=title,
                        content=content,
                        status="delivered" if success else "failed",
                    )
                    session.add(channel_notification)
                    logger.info(f"Notification via {channel}: {status_msg}")
        except Exception as exc:
            logger.warning(f"Failed to send external notifications: {exc}")

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
