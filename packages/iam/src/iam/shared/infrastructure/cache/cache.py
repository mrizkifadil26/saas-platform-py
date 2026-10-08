from dataclasses import dataclass
from datetime import timedelta
from typing import Protocol


class CacheStore(Protocol):
    async def get(self, key: str) -> bytes | None: ...

    async def set(self, key: str, value: bytes, *, ttl: timedelta) -> None: ...

    async def delete(self, key: str) -> None: ...


@dataclass(frozen=True, slots=True)
class CacheKey:
    namespace: str

    def build(
        self,
        region: str,
        identifier: str,
    ) -> str:
        return f"{self.namespace}:{region}:{identifier}"
