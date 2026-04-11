"""Alarm and notification ORM models."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class AlarmRecord(TimestampMixin, Base):
    """Alarm events derived from device telemetry."""

    __tablename__ = "alarms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_id: Mapped[str] = mapped_column(String(15), ForeignKey("devices.device_id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    alarm_type: Mapped[int] = mapped_column(Integer, index=True)
    battery: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(String(255))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    device = relationship("Device", back_populates="alarms")

    __table_args__ = (
        # Composite index for alarm list queries filtering by device_id and ordering by timestamp
        Index("ix_alarms_device_timestamp", "device_id", "timestamp"),
    )


class NotificationRecord(TimestampMixin, Base):
    """Notification delivery log for alarms."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_id: Mapped[str] = mapped_column(String(15), ForeignKey("devices.device_id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    channel: Mapped[str] = mapped_column(String(30), default="in_app")
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="queued")

    device = relationship("Device", back_populates="notifications")
