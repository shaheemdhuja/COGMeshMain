"""MessageLog ORM Model representing audit log entries for RuntimeMessages."""

from datetime import datetime, timezone
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, UUIDMixin


class MessageLog(Base, UUIDMixin):
    """Represents an audit log record of a transmitted RuntimeMessage."""

    __tablename__ = "message_logs"

    message_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_node: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    destination_node: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
