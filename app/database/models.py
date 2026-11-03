
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime

from app.database.connection import Base


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, nullable=False, index=True)
    payload = Column(Text, nullable=False)
    status = Column(String, default="pending", nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    published_at = Column(DateTime(timezone=True), nullable=True)
