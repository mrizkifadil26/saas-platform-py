from dataclasses import asdict
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db import AppBase
from iam.shared.domain import DomainEvent


class OutboxEventModel(AppBase):
    __tablename__ = "iam_outbox_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


def serialize_domain_event(
    event: DomainEvent,
) -> dict[str, Any]:
    return {
        "event_type": type(event).__name__,
        "payload": asdict(event),
        "occurred_at": event.occurred_at,
    }
