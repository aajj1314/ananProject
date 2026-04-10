"""Alarm and notification ORM models."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AlarmRecord(Base):
    """Alarm events derived from device telemetry."""

    __tablename__ = "alarms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_id: Mapped[str] = mapped_column(String(15), index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    alarm_type: Mapped[int] = mapped_column(Integer, index=True)
    battery: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(String(255))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class NotificationRecord(Base):
    """Notification delivery log for alarms."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_id: Mapped[str] = mapped_column(String(15), index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    channel: Mapped[str] = mapped_column(String(30), default="in_app")
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="queued")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
