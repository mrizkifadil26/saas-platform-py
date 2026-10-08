from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Generic, TypeVar
from uuid import UUID, uuid4

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class MessageMetadata:
    message_id: UUID
    occurred_at: datetime

    # correlation_id: UUID | None = None
    # causation_id: UUID | None = None

    # schema_version: int = 1
    # headers: dict[str, str] = field(default_factory=lambda: dict[str, str]())

    @classmethod
    def create(
        cls,
        # *,
        # correlation_id: UUID | None = None,
        # causation_id: UUID | None = None,
        # schema_version: int = 1,
        # headers: dict[str, str] | None = None,
    ) -> MessageMetadata:
        return cls(
            message_id=uuid4(),
            occurred_at=datetime.now(UTC),
            # correlation_id=correlation_id,
            # causation_id=causation_id,
            # schema_version=schema_version,
            # headers=headers or {},
        )


@dataclass(frozen=True, slots=True)
class MessageEnvelope(Generic[T]):
    message_type: str
    payload: T
    metadata: MessageMetadata
