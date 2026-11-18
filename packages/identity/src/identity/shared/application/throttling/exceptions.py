from datetime import timedelta


class RateLimitExceeded(Exception):
    def __init__(
        self,
        *,
        retry_after: timedelta | None = None,
    ) -> None:
        self.retry_after = retry_after

        super().__init__("rate limit exceeded")
