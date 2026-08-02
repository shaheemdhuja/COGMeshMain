"""ConnectionLog ORM Model representing connection audit history events."""

from datetime import datetime, timezone
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, UUIDMixin


class ConnectionLog(Base, UUIDMixin):
    """Represents an audit entry of node connection lifecycle events."""

    __tablename__ = "connection_logs"

    node_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    transport: Mapped[str] = mapped_column(String(50), default="WEBSOCKET", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
