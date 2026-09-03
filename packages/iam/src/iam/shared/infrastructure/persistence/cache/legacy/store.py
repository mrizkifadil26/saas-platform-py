from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

from iam.shared.application.cache import Cache

from .region import CacheRegion

T = TypeVar("T")


@dataclass(slots=True)
class CacheRegionStore(Generic[T]):
    cache: Cache
    region: CacheRegion
    serialize: Callable[[T], bytes]
    deserialize: Callable[[bytes], T]

    async def get(
        self,
        *key_parts: object,
    ) -> T | None: ...

    async def set(
        self,
        value: T,
        *key_parts: object,
    ) -> None: ...

    async def delete(
        self,
        *key_parts: object,
    ) -> None: ...
