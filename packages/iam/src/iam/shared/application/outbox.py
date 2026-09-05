from typing import Any, Protocol
from uuid import UUID


class OutboxWriter(Protocol):
    async def add(
        self,
        *,
        id: UUID,
        topic: str,
        payload: dict[str, Any],
    ) -> None: ...


class OutboxHandler(Protocol):
    async def handle(
        self,
        message: Any,
    ) -> None: ...


class OutboxRepository(Protocol):
    async def claim_batch(self, limit: int) -> list[dict[str, Any]]: ...

    async def mark_failed(self, message_id: UUID, error: str) -> None: ...

    async def mark_published(self, message_id: UUID) -> None: ...
