from typing import Protocol


class CacheStore(Protocol):
    async def get(self, key: str) -> bytes | None: ...

    async def set(
        self,
        key: str,
        value: bytes,
        *,
        ttl: int | None = None,
    ) -> None: ...

    async def delete(self, key: str) -> None: ...
