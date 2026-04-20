from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from billing.domain.payg.entities import PaygPurchase


class Clock(Protocol):
    def now(self) -> datetime: ...


class EventPublisher(Protocol):
    def publish(self, event: object) -> None: ...


class PaygPurchaseRepository(Protocol):
    def save(self, purchase: PaygPurchase) -> None: ...


@dataclass(frozen=True, slots=True)
class SystemClock:
    def now(self) -> datetime:
        from billing.domain.shared.time import utc_now

        return utc_now()
