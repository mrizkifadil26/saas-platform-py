from redis.asyncio import Redis

from iam.shared.application.cache import Cache


class RedisCache(Cache):
    def __init__(
        self,
        redis: Redis,
    ) -> None:
        self._redis = redis

    async def get(
        self,
        key: str,
    ) -> str | None:
        return await self._redis.get(key)

    async def set(
        self,
        key: str,
        value: str,
        *,
        ttl: int | None = None,
    ) -> None:
        await self._redis.set(
            key,
            value,
            ex=ttl,
        )

    async def delete(
        self,
        key: str,
    ) -> None:
        await self._redis.delete(key)

    async def delete_pattern(self, key: str) -> None:
        raise NotImplementedError
