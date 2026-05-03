from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from billing.credits.domain.value_objects.credits import Credits
from billing.payg.domain.value_objects.pack_code import PackCode
from billing.shared.domain.value_objects.money import Money
from billing.subscription.domain.value_objects.plan_code import PlanCode


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


@dataclass(frozen=True, slots=True)
class SubscriptionPlan:
    # TODO: need to decide whether to use PlanId or PlanCode here. PlanId is more generic, but PlanCode is more specific to subscription plans.
    code: PlanCode
    name: str
    included_credits: Credits
    price: Money


@dataclass(frozen=True, slots=True)
class PaygCreditPackage:
    code: PackCode
    name: str
    credits: Credits
    price: Money
