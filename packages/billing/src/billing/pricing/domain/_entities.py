from dataclasses import dataclass
from datetime import datetime
from typing import NewType

from billing.credits.domain.value_objects.credits import Credits
from billing.payg.domain.value_objects import PackCode
from billing.pricing.exceptions import (
    InvalidPlanConfiguration,
    PricingNotFound,
)
from billing.shared.domain.enums import (
    BillingInterval,
    UsageMetric,
)
from billing.shared.domain.value_objects.money import Money
from billing.subscription.domain.plans import PlanCode
from billing.subscription.domain.value_objects.product_code import ProductCode


@dataclass(frozen=True, slots=True)
class SubscriptionPlan:
    code: PlanCode
    name: str
    interval: BillingInterval
    price: Money
    included_credits: Credits
    active: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidPlanConfiguration("plan name cannot be blank")
        if self.price.is_negative():
            raise InvalidPlanConfiguration("plan price cannot be negative")
        if int(self.included_credits) < 0:
            raise InvalidPlanConfiguration("included credits cannot be negative")


@dataclass(frozen=True, slots=True)
class PaygPack:
    code: PackCode
    name: str
    price: Money
    credits: Credits
    expires_in_days: int
    active: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidPlanConfiguration("pack name cannot be blank")
        if self.price.is_negative():
            raise InvalidPlanConfiguration("pack price cannot be negative")
        if int(self.credits) <= 0:
            raise InvalidPlanConfiguration("pack credits must be positive")
        if self.expires_in_days <= 0:
            raise InvalidPlanConfiguration("pack expiry days must be positive")


@dataclass(frozen=True, slots=True)
class UsagePriceRule:
    product_code: ProductCode
    metric: UsageMetric
    credits_per_unit: Credits
    effective_from: datetime
    effective_to: datetime | None = None

    def __post_init__(self) -> None:
        if int(self.credits_per_unit) < 0:
            raise InvalidPlanConfiguration("credits_per_unit cannot be negative")

    def is_effective_at(self, at: datetime) -> bool:
        if at < self.effective_from:
            return False
        if self.effective_to is not None and at >= self.effective_to:
            return False
        return True

    def calculate_cost(self, quantity: int) -> Credits:
        if quantity < 0:
            raise InvalidPlanConfiguration("quantity cannot be negative")
        return Credits(int(self.credits_per_unit) * quantity)


@dataclass(frozen=True, slots=True)
class PricingCatalog:
    subscription_plans: tuple[SubscriptionPlan, ...]
    payg_packs: tuple[PaygPack, ...]
    usage_rules: tuple[UsagePriceRule, ...]

    def get_plan(self, code: PlanCode) -> SubscriptionPlan:
        for plan in self.subscription_plans:
            if plan.code == code and plan.active:
                return plan

        raise PricingNotFound(f"active plan not found: {code}")

    def get_pack(self, code: PackCode) -> PaygPack:
        for pack in self.payg_packs:
            if pack.code == code and pack.active:
                return pack
        raise PricingNotFound(f"active payg pack not found: {code}")

    def get_usage_rule(self, product_code: ProductCode, at: datetime) -> UsagePriceRule:
        matches = [
            rule
            for rule in self.usage_rules
            if rule.product_code == product_code and rule.is_effective_at(at)
        ]
        if not matches:
            raise PricingNotFound(f"usage rule not found for product: {product_code}")
        matches.sort(key=lambda r: r.effective_from, reverse=True)
        return matches[0]
