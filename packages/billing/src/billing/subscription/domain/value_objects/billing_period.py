from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True, slots=True)
class BillingPeriod:
    start_at: datetime
    end_at: datetime

    def __post_init__(self) -> None:
        if self.start_at.tzinfo is None or self.end_at.tzinfo is None:
            raise ValueError("BillingPeriod datetimes must be timezone-aware")

        if self.end_at <= self.start_at:
            raise ValueError("BillingPeriod end_at must be after start_at")

    @property
    def duration(self) -> timedelta:
        return self.end_at - self.start_at

    def contains(self, moment: datetime) -> bool:
        if moment.tzinfo is None:
            raise ValueError("Moment datetime must be timezone-aware")

        return self.start_at <= moment < self.end_at

    def overlaps(self, other: BillingPeriod) -> bool:
        return self.start_at < other.end_at and other.start_at < self.end_at

    def is_adjacent_to(self, other: BillingPeriod) -> bool:
        return self.end_at == other.start_at or other.end_at == self.start_at

    def next_period(self, interval: BillingPeriod) -> BillingPeriod:
        duration = self.duration
        return BillingPeriod(
            start_at=self.end_at,
            end_at=self.end_at + duration,
        )

    @classmethod
    def from_bounds(cls, start_at: datetime, end_at: datetime) -> "BillingPeriod":
        return cls(start_at=start_at, end_at=end_at)

    @classmethod
    def utc_month(
        cls,
        year: int,
        month: int,
    ) -> BillingPeriod:
        start = datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end = datetime(year, month + 1, 1, tzinfo=timezone.utc)

        return cls(start_at=start, end_at=end)

    # def cycle_key(self, subscription_id: SubscriptionId) -> str:
    #     return f"{subscription_id.value}:{self.start_at.date().isoformat()}:{self.end_at.date().isoformat()}"
