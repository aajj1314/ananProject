"""Location ORM model."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class LocationRecord(TimestampMixin, Base):
    """Relational location fallback for recent and historical queries."""

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_id: Mapped[str] = mapped_column(String(15), ForeignKey("devices.device_id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    altitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    battery: Mapped[int] = mapped_column(Integer)
    alarm_type: Mapped[int] = mapped_column(Integer, default=0)
    fence_events: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    device = relationship("Device", back_populates="locations")

    __table_args__ = (
        # Composite index for history queries that filter by device_id AND timestamp range
        Index("ix_locations_device_timestamp", "device_id", "timestamp"),
    )
