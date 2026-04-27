from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class GetPricingRuleQuery:
    pricing_key: str
    at: datetime


@dataclass(frozen=True, slots=True)
class CreatePricingSnapshotQuery:
    pricing_key: str
    at: datetime
