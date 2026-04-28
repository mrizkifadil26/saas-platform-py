from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class PricingRuleDTO:
    id: UUID
    pricing_key: str
    unit_amount: Decimal
    currency_code: str
    billing_scheme: str
    active_from: datetime
    active_until: datetime | None


@dataclass(frozen=True, slots=True)
class PricingSnapshotDTO:
    pricing_rule_id: UUID
    pricing_key: str
    unit_amount: Decimal
    currency_code: str
    billing_scheme: str
    captured_at: datetime
