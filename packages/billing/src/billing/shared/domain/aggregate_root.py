from dataclasses import dataclass, field
from typing import Generic, TypeVar

from billing.shared.domain.domain_event import DomainEvent

IdT = TypeVar("IdT")


@dataclass(frozen=True, slots=True)
class AggregateRoot(Generic[IdT]):
    _domain_events: list[DomainEvent] = field(
        default_factory=list,
        init=False,
        repr=False,
        compare=False,
    )

    @property
    def domain_events(self) -> tuple[DomainEvent, ...]:
        return tuple(self._domain_events)

    def record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def pull_domain_events(self) -> tuple[DomainEvent, ...]:
        events = tuple(self._domain_events)
        self._domain_events.clear()
        return events

    def clear_domain_events(self) -> None:
        self._domain_events.clear()
