"""Location schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DeviceTelemetryIn(BaseModel):
    """Telemetry payload uploaded by a device."""

    device_id: str = Field(min_length=15, max_length=15)
    timestamp: datetime
    latitude: float
    longitude: float
    altitude: float | None = None
    alarm_type: int = Field(ge=0, le=5, default=0)
    battery: int = Field(ge=0, le=100)
    speed: float | None = None
    direction: int | None = Field(default=None, ge=0, le=360)

    @field_validator("device_id")
    @classmethod
    def validate_device_id(cls, value: str) -> str:
        """Ensure IMEI format."""

        if not value.isdigit():
            raise ValueError("Device ID must contain exactly 15 digits")
        return value

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, value: float) -> float:
        """Ensure latitude is valid."""

        if not -90 <= value <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        return value

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, value: float) -> float:
        """Ensure longitude is valid."""

        if not -180 <= value <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        return value


class LocationRead(BaseModel):
    """Single location payload."""

    device_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    altitude: float | None = None
    speed: float | None = None
    battery: int
    alarm_type: int
    fence_events: list[dict] | None = None

    model_config = ConfigDict(from_attributes=True)


class HistorySummary(BaseModel):
    """History summary payload."""

    device_id: str
    total_points: int
    start_time: datetime
    end_time: datetime
    latest_battery: int | None = None
    alarms_detected: int
    last_alarm_type: int | None = None
