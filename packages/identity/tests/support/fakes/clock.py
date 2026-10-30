from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(slots=True)
class FakeClock:
    current: datetime

    def now(self) -> datetime:
        return self.current

    def set(self, value: datetime) -> None:
        self.current = value

    def advance(self, delta: timedelta) -> None:
        self.current += delta
