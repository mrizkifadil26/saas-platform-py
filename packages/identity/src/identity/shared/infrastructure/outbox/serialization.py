from typing import Any, Protocol

from identity.shared.kernel.events import DomainEvent

from .exceptions import (
    EventTypeAlreadyRegisteredError,
    UnknownEventTypeError,
)


class EventSerializer(Protocol):
    def serialize(self, event: DomainEvent) -> dict[str, Any]: ...

    def deserialize(
        self,
        payload: dict[str, Any],
        event_type: str,
    ) -> DomainEvent: ...


class EventRegistry:
    def __init__(self) -> None:
        self._events: dict[str, type[DomainEvent]] = {}

    def register(
        self,
        event_type: str,
        event_class: type[DomainEvent],
    ) -> None:
        if event_type in self._events:
            raise EventTypeAlreadyRegisteredError(event_type)

        self._events[event_type] = event_class

    def resolve(
        self,
        event_type: str,
    ) -> type[DomainEvent]:
        try:
            return self._events[event_type]
        except KeyError:
            raise UnknownEventTypeError(event_type) from None

    def register_event(
        self,
        event_class: type[DomainEvent],
    ) -> None:
        self.register(
            event_type=event_class.event_type,
            event_class=event_class,
        )
