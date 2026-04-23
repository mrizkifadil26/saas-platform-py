from typing import Protocol


class IdempotencyStore(Protocol):
    async def get(self, key: str) -> str | None:
        raise NotImplementedError

    async def save(
        self,
        key: str,
        fingerprint: str,
    ) -> None:
        raise NotImplementedError
