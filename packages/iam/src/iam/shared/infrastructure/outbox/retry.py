from dataclasses import dataclass
from datetime import datetime, timedelta

from iam.shared.infrastructure.outbox.publisher import OutboxRetryPolicy


@dataclass(frozen=True, slots=True)
class RetryPolicy(OutboxRetryPolicy):
    base_delay: timedelta = timedelta(seconds=5)
    max_delay: timedelta = timedelta(minutes=15)

    def retry_at(
        self,
        *,
        now: datetime,
        attempts: int,
    ) -> datetime:
        exponent = max(attempts - 1, 0)

        delay = self.base_delay * (2**exponent)

        if delay > self.max_delay:
            delay = self.max_delay

        return now + delay
