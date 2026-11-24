from __future__ import annotations

import redis.asyncio as redis
from redis.asyncio import Redis

from .settings import RedisSettings


class RedisClient:
    def __init__(self, client: Redis) -> None:
        self._client = client

    @classmethod
    def create(
        cls,
        settings: RedisSettings,
    ) -> RedisClient:
        client = redis.from_url(
            settings.url,
            decode_responses=True,
        )

        return cls(client)

    @property
    def client(self) -> Redis:
        return self._client

    async def close(self) -> None:
        await self._client.aclose()

    async def health(self) -> None:
        await self._client.ping()  # type: ignore
