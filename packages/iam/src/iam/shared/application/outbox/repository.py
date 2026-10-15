from collections.abc import Sequence
from datetime import datetime
from typing import Any, Protocol, TypeVar
from uuid import UUID

from iam.shared.application.messaging.message import MessageEnvelope

from .message import OutboxMessage

T = TypeVar("T")


class OutboxRepository(Protocol):
    async def add(
        self,
        message: MessageEnvelope[Any],
    ) -> None: ...

    async def claim(
        self,
        *,
        limit: int,
        worker_id: str,
        lease_until: datetime,
    ) -> Sequence[OutboxMessage]: ...

    async def mark_published(
        self,
        *,
        message_id: UUID,
    ) -> None: ...

    async def mark_failed(
        self,
        *,
        message_id: UUID,
        available_at: datetime,
        error: str,
    ) -> None: ...
