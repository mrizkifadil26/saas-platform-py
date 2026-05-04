from dataclasses import dataclass, field
from typing import Generic, TypeVar

from iam.shared.domain.domain_event import DomainEvent
from iam.shared.domain.entity import Entity


AggregateId = TypeVar("AggregateId")


@dataclass(eq=False)
class AggregateRoot(Entity[AggregateId], Generic[AggregateId]):
    _events: list[DomainEvent] = field(default_factory=list, init=False)

    def record_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        events = self._events.copy()
        self._events.clear()
        return events
