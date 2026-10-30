from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from identity.accounts.infrastructure.database.repositories import func
from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class OutboxMessageModel(DeclarativeBase):
    __tablename__ = "outbox_messages"

    Index(
        "ix_outbox_pending",
        "published_at",
        # "type",
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    message_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    aggregate_type: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    aggregate_id: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    available_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class OutboxDLQModel(DeclarativeBase):
    __tablename__ = "outbox_dlq"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    original_message_id: Mapped[UUID] = mapped_column(
        nullable=False,
    )

    topic: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    failed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
