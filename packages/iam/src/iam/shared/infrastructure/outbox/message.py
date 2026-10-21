from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from iam.shared.kernel.events import DomainEvent

from .serialization import EventSerializer


@dataclass(frozen=True, slots=True)
class OutboxMessage:
    id: UUID

    message_type: str
    payload: dict[str, Any]
    occurred_at: datetime

    aggregate_type: str | None = None
    aggregate_id: str | None = None

    published_at: datetime | None = None
    attempts: int = 0
    available_at: datetime | None = None
    locked_until: datetime | None = None


class OutboxMessageFactory:
    def __init__(
        self,
        serializer: EventSerializer,
    ) -> None:
        self._serializer = serializer

    def from_event(
        self,
        event: DomainEvent,
        *,
        aggregate_id: str | None = None,
        aggregate_type: str | None = None,
        # headers: dict[str, str] | None = None,
    ) -> OutboxMessage:
        return OutboxMessage(
            id=event.event_id,
            message_type=event.event_type,
            payload=self._serializer.serialize(event),
            occurred_at=event.occurred_at,
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            # headers=headers or {},
        )
