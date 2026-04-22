from typing import Protocol

from billing.domain.credits.value_objects import ProductCode
from billing.domain.payg.value_objects import PackCode
from billing.domain.pricing.models import (
    PaygPack,
    SubscriptionPlan,
    UsagePriceRule,
)
from billing.domain.shared.value_objects import PlanCode


class SubscriptionPlanRepository(Protocol):
    async def get_active(
        self, code: PlanCode
    ) -> SubscriptionPlan: ...


class PaygPackRepository(Protocol):
    async def get_active(
        self, code: PackCode
    ) -> PaygPack: ...


class UsagePriceRuleRepository(Protocol):
    async def get_effective(
        self, product_code: ProductCode, at
    ) -> UsagePriceRule: ...
