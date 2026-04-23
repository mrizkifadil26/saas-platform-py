from typing import Generic, TypeVar

from billing.shared.domain.domain_event import DomainEvent
from billing.shared.domain.entity import Entity

IdT = TypeVar("IdT")


class AggregateRoot(Entity[IdT], Generic[IdT]):
    def __init__(self, entity_id: IdT) -> None:
        super().__init__(entity_id)
        self._domain_events: list[DomainEvent] = []

    @property
    def domain_events(self) -> tuple[DomainEvent, ...]:
        return tuple(self._domain_events)

    def record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def pull_domain_events(self) -> tuple[DomainEvent, ...]:
        events = self.domain_events
        self._domain_events.clear()
        return events

    def clear_domain_events(self) -> None:
        self._domain_events.clear()
