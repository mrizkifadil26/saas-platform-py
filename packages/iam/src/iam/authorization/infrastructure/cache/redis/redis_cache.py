from redis import Redis

from iam.authorization.infrastructure.cache import Cache


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
        value = await self._redis.get(key)
        if value is None:
            return None

        return value.decode()

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
