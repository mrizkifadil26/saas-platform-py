from collections.abc import Mapping
from dataclasses import asdict
from datetime import date, datetime
from enum import Enum
from typing import Any, cast
from uuid import UUID

from identity.shared.infrastructure.outbox.exceptions import (
    EventSerializationError,
    InvalidEventPayloadError,
)
from identity.shared.infrastructure.outbox.serialization import EventRegistry
from identity.shared.kernel.events import DomainEvent


class JsonEventSerializer:
    def __init__(
        self,
        registry: EventRegistry,
    ) -> None:
        self._registry = registry

    def serialize(
        self,
        event: DomainEvent,
    ) -> dict[str, Any]:
        try:
            payload = asdict(event)

            return cast(
                dict[str, Any],
                self._encode(payload),
            )

        except (TypeError, ValueError) as exc:
            raise EventSerializationError(
                f"Failed to serialize event {event.event_type!r}"
            ) from exc

    def deserialize(
        self,
        payload: dict[str, Any],
        event_type: str,
    ) -> DomainEvent:
        event_class = self._registry.resolve(event_type)

        try:
            return event_class(**payload)
        except (TypeError, ValueError) as exc:
            raise InvalidEventPayloadError(
                f"Invalid payload for event "  # code-split
                f"{event_type!r}"
            ) from exc

    @classmethod
    def _encode(cls, value: object) -> Any:
        if isinstance(value, UUID):
            return str(value)

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, Enum):
            return cls._encode(value.value)

        if isinstance(value, Mapping):
            data = cast(dict[object, object], value)
            return {str(key): cls._encode(item) for key, item in data.items()}

        if isinstance(value, (list, tuple)):
            items = cast(list[object] | tuple[object, ...], value)
            return [cls._encode(item) for item in items]

        if value is None or isinstance(value, (str, int, float, bool)):
            return value

        raise TypeError(f"Unsupported event value: {type(value).__name__}")
