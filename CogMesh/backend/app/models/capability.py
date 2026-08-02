"""Capability ORM Model representing device hardware and AI execution profiles."""

from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.device import Device


class Capability(Base, UUIDMixin, TimestampMixin):
    """Represents hardware and software capabilities exported by a device."""

    __tablename__ = "capabilities"

    device_id: Mapped[str] = mapped_column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    capability_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., OCR, LLM, TRANSLATION, CPU_COMPUTE
    specs: Mapped[dict] = mapped_column(JSON, nullable=False)  # Telemetry JSON (RAM, VRAM, models installed, battery)

    # Relationships
    device: Mapped["Device"] = relationship("Device", back_populates="capabilities")
