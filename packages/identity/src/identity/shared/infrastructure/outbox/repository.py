from collections.abc import Sequence
from datetime import datetime
from typing import Protocol
from uuid import UUID

from identity.shared.kernel.events import DomainEvent

from .message import OutboxMessage


class OutboxWriter(Protocol):
    async def add(
        self,
        message: OutboxMessage,
    ) -> None: ...

    async def add_all(
        self,
        messages: Sequence[OutboxMessage],
    ) -> None: ...

    async def add_event(
        self,
        event: DomainEvent,
    ) -> None: ...

    async def add_events(
        self,
        events: Sequence[DomainEvent],
    ) -> None: ...


class OutboxPublisherRepository(Protocol):
    async def claim_batch(
        self,
        *,
        limit: int,
        now: datetime,
        locked_until: datetime,
    ) -> Sequence[OutboxMessage]: ...

    async def mark_published(
        self,
        message_id: UUID,
        *,
        published_at: datetime,
    ) -> bool: ...

    async def mark_failed(
        self,
        message_id: UUID,
        *,
        error: str,
        retry_at: datetime,
    ) -> None: ...
