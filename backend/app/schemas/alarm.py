"""Alarm schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlarmLatestRead(BaseModel):
    """Latest alarm state payload for a device."""

    device_id: str
    alarm_type: int
    battery: int
    timestamp: datetime


class AlarmRead(BaseModel):
    """Alarm event payload."""

    id: int
    device_id: str
    user_id: int
    alarm_type: int
    battery: int
    message: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationRead(BaseModel):
    """Notification log payload."""

    id: int
    device_id: str
    user_id: int
    channel: str
    title: str
    content: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
