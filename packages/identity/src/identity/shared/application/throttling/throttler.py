from dataclasses import dataclass
from typing import Iterable

from identity.shared.application.throttling.exceptions import RateLimitExceeded

from .contracts import RateLimit, RateLimiter
from .policy import TContext, ThrottleRule


@dataclass(slots=True)
class Throttler:
    limiter: RateLimiter

    async def enforce(
        self,
        rules: Iterable[ThrottleRule[TContext]],
        *,
        context: TContext,
    ) -> None:
        for rule in rules:
            identifier = rule.key(context)

            result = await self.limiter.consume(
                key=f"{rule.namespace}:{identifier}",
                rate_limit=RateLimit(
                    limit=rule.limit,
                    window=rule.window,
                ),
            )

            if not result.allowed:
                raise RateLimitExceeded(
                    retry_after=result.retry_after,
                )
