from datetime import datetime, timezone

from billing.shared.application.clock import Clock


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
