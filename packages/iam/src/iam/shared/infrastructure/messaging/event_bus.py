from collections.abc import Awaitable, Callable
from typing import Type

from iam.shared.domain import DomainEvent

EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[Type[DomainEvent], list[EventHandler]] = {}

    def subscribe(
        self,
        event_type: Type[DomainEvent],
        handler: EventHandler,
    ) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    async def publish(self, events: list[DomainEvent]) -> None:
        for event in events:
            for handler in self._handlers.get(type(event), []):
                await handler(event)
