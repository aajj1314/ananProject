"""Device schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DeviceCreate(BaseModel):
    """Bind device request."""

    device_id: str = Field(min_length=15, max_length=15)
    device_name: str = Field(min_length=1, max_length=100)

    @field_validator("device_id")
    @classmethod
    def validate_device_id(cls, value: str) -> str:
        """Ensure IMEI-style device identifier."""

        if not value.isdigit():
            raise ValueError("Device ID must contain exactly 15 digits")
        return value


class DeviceUpdate(BaseModel):
    """Update device metadata."""

    device_name: str = Field(min_length=1, max_length=100)


class DeviceRead(BaseModel):
    """Device response payload."""

    device_id: str
    device_name: str
    battery: int
    last_latitude: float | None = None
    last_longitude: float | None = None
    last_updated: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
