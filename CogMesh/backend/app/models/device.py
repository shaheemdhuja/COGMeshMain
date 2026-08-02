"""Device ORM Model representing edge devices in the mesh."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.capability import Capability
    from app.models.task import Task
    from app.models.task_log import TaskLog


class Device(Base, UUIDMixin, TimestampMixin):
    """Represents a discovered or registered edge device node in CogMesh."""

    __tablename__ = "devices"

    device_name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., LAPTOP, PHONE, TABLET
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False, default=8000)
    status: Mapped[str] = mapped_column(String(50), default="OFFLINE", index=True, nullable=False)  # ONLINE, OFFLINE, BUSY
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    capabilities: Mapped[List["Capability"]] = relationship("Capability", back_populates="device", cascade="all, delete-orphan")
    assigned_tasks: Mapped[List["Task"]] = relationship("Task", back_populates="assigned_device")
    task_logs: Mapped[List["TaskLog"]] = relationship("TaskLog", back_populates="device")
