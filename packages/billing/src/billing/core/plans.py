from dataclasses import dataclass
from typing import Literal, Optional

from .types import Credits, PlanCode

PlanKind = Literal["subscription", "payg"]


@dataclass(frozen=True)
class Plan:
    code: PlanCode
    kind: PlanKind
    tier: str
    price_cents: int
    currency: str = "usd"
    billing_interval: Optional[str] = None
    credits_grant: Credits = Credits(0)
