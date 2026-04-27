from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class PriceResponse(BaseModel):
    amount: Decimal
    currency: str


class PricingRuleResponse(BaseModel):
    id: UUID
    pricing_key: str
    amount: Decimal
    currency: str
    billing_scheme: str
    active_from: datetime
    active_until: datetime | None


class PricingSnapshotResponse(BaseModel):
    pricing_rule_id: UUID
    pricing_key: str
    unit_amount: Decimal
    currency: str
    billing_scheme: str
    captured_at: datetime
