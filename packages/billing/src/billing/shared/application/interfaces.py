from typing import Protocol


class EventPublisher(Protocol):
    async def publish(self, event: object) -> None:
        raise NotImplementedError

    async def publish_many(
        self,
        events: list[object],
    ) -> None:
        raise NotImplementedError


class IdempotencyStore(Protocol):
    async def get(self, key: str) -> str | None:
        raise NotImplementedError

    async def save(
        self,
        key: str,
        fingerprint: str,
    ) -> None:
        raise NotImplementedError
