from datetime import timedelta

from redis.asyncio import Redis

from .cache import CacheStore


class RedisCacheStore(CacheStore):
    def __init__(
        self,
        client: Redis,
    ) -> None:
        self._client = client

    async def get(
        self,
        key: str,
    ) -> bytes | None:
        return await self._client.get(key)

    async def set(
        self,
        key: str,
        value: bytes,
        *,
        ttl: timedelta,
    ) -> None:
        await self._client.set(key, value, ex=int(ttl.total_seconds()))

    async def delete(
        self,
        key: str,
    ) -> None:
        await self._client.delete(key)
