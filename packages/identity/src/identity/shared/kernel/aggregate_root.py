from dataclasses import dataclass, field
from typing import TypeVar

from .entity import Entity
from .events import DomainEvent

AggregateIdT = TypeVar("AggregateIdT")


@dataclass(eq=False)
class AggregateRoot(Entity[AggregateIdT]):
    _events: list[DomainEvent] = field(
        default_factory=lambda: [],
        init=False,
        repr=False,
    )

    def record_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        events = self._events.copy()
        self._events.clear()
        return events
