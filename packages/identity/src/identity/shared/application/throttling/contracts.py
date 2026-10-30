from dataclasses import dataclass
from datetime import timedelta
from typing import Protocol


@dataclass(frozen=True, slots=True)
class RateLimit:
    limit: int
    window: timedelta

    def __post_init__(self) -> None:
        if self.limit <= 0:
            raise ValueError("limit must be greater than zero")

        if self.window.total_seconds() <= 0:
            raise ValueError("window must be greater than zero")


@dataclass(frozen=True, slots=True)
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after: timedelta | None


class RateLimiter(Protocol):
    async def check(
        self,
        *,
        key: str,
        rate_limit: RateLimit,
    ) -> RateLimitResult: ...

    async def consume(
        self,
        *,
        key: str,
        rate_limit: RateLimit,
    ) -> RateLimitResult: ...
