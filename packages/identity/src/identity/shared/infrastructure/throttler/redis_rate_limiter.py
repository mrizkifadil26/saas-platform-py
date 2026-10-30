from datetime import timedelta
from typing import Tuple, cast

from identity.shared.application.throttling.contracts import RateLimit, RateLimiter, RateLimitResult
from redis.asyncio import Redis
from redis.commands.core import AsyncScript

_CONSUME_SCRIPT = """
local current = redis.call("INCR", KEYS[1])

if current == 1 then
    redis.call("PEXPIRE", KEYS[1], ARGV[1])
end

local ttl = redis.call("PTTL", KEYS[1])

return {current, ttl}
"""


class RedisRateLimiter(RateLimiter):
    def __init__(self, redis: Redis) -> None:
        self._redis = redis
        self._consume: AsyncScript = self._redis.register_script(
            _CONSUME_SCRIPT,
        )

    async def check(
        self,
        *,
        key: str,
        rate_limit: RateLimit,
    ) -> RateLimitResult:
        current = await self._redis.get(key)

        if current is None:
            return RateLimitResult(
                allowed=True,
                limit=rate_limit.limit,
                remaining=rate_limit.limit,
                retry_after=None,
            )

        current = int(current)

        ttl_ms = await self._redis.pttl(key)
        allowed = current < rate_limit.limit
        remaining = max(
            rate_limit.limit - current,
            0,
        )

        retry_after = None
        if not allowed:
            retry_after = timedelta(
                milliseconds=max(ttl_ms, 0),
            )

        return RateLimitResult(
            allowed=allowed,
            limit=rate_limit.limit,
            remaining=remaining,
            retry_after=retry_after,
        )

    async def consume(
        self,
        *,
        key: str,
        rate_limit: RateLimit,
    ) -> RateLimitResult:
        window_ms = int(rate_limit.window.total_seconds() * 1000)

        current, ttl_ms = cast(
            Tuple[int, int],
            await self._consume(
                keys=[key],
                args=[window_ms],
            ),
        )

        current = int(current)
        ttl_ms = int(ttl_ms)

        allowed = current <= rate_limit.limit

        remaining = max(
            rate_limit.limit - current,
            0,
        )

        retry_after = None
        if not allowed:
            retry_after = timedelta(milliseconds=max(ttl_ms, 0))

        return RateLimitResult(
            allowed=allowed,
            limit=rate_limit.limit,
            remaining=remaining,
            retry_after=retry_after,
        )
