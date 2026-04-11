"""Notification persistence service."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alarm import NotificationRecord


class NotificationService:
    """Create notification delivery records."""

    @staticmethod
    async def create_alarm_notification(
        device_id: str,
        user_id: int,
        alarm_type: int,
        battery: int,
        session: AsyncSession,
        *,
        title: str | None = None,
        content: str | None = None,
    ) -> NotificationRecord:
        """Persist a notification log for an alarm event."""

        notification = NotificationRecord(
            device_id=device_id,
            user_id=user_id,
            channel="in_app",
            title=title or f"设备报警 {alarm_type}",
            content=content or f"设备 {device_id} 触发报警 {alarm_type}，当前电量 {battery}%",
            status="queued",
        )
        session.add(notification)
        await session.flush()
        return notification
