from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class OutboxMessage:
    # message: MessageEnvelope[Any]
    # attempts: int
    # available_at: datetime

    id: UUID
    topic: str
    event_type: str
    payload: dict[str, object]
    occurred_at: datetime

    aggregate_type: str | None = None
    aggregate_id: str | None = None

    published_at: datetime | None = None
    attempts: int = 0
    available_at: datetime | None = None


@dataclass(frozen=True)
class EventEnvelope:
    id: UUID
    event_type: str
    topic: str
    payload: dict
    occurred_at: datetime

    aggregate_type: str | None = None
    aggregate_id: str | None = None
