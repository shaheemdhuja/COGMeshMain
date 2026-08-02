"""Capability ORM Model representing device hardware and AI execution capabilities."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.device import Device


class Capability(Base, UUIDMixin, TimestampMixin):
    """Stores the latest hardware and software capability snapshot for a registered edge device."""

    __tablename__ = "capabilities"

    device_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    cpu_cores: Mapped[int] = mapped_column(Integer, nullable=False)
    ram_gb: Mapped[float] = mapped_column(Float, nullable=False)
    battery_level: Mapped[float] = mapped_column(Float, nullable=False)  # 0 to 100 percentage
    network_quality: Mapped[str] = mapped_column(String(50), nullable=False, default="GOOD")
    supported_tasks: Mapped[List[str]] = mapped_column(JSON, nullable=False)  # e.g., ["OCR", "SUMMARIZATION", "TRANSLATION"]
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    device: Mapped["Device"] = relationship("Device", back_populates="capability")
