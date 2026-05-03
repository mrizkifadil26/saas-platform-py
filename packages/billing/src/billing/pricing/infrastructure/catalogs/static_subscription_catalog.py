from decimal import Decimal

from billing.credits.domain.value_objects.credits import Credits
from billing.pricing.application.catalogs import SubscriptionPricingCatalog
from billing.pricing.application.dto import SubscriptionPlan
from billing.pricing.domain.exceptions import PricingNotFound
from billing.shared.domain.value_objects.currency import Currency
from billing.shared.domain.value_objects.money import Money
from billing.subscription.domain.value_objects.plan_code import PlanCode


class StaticSubscriptionCatalog(SubscriptionPricingCatalog):
    def __init__(self) -> None:
        self._plans: dict[PlanCode, SubscriptionPlan] = {
            PlanCode("sub_basic_monthly"): SubscriptionPlan(
                code=PlanCode("sub_basic_monthly"),
                name="Basic Monthly",
                # interval=BillingInterval.MONTH,
                included_credits=Credits(1000),
                price=Money(amount=Decimal("99.00"), currency=Currency.USD),
            ),
            PlanCode("sub_pro_monthly"): SubscriptionPlan(
                code=PlanCode("sub_pro_monthly"),
                name="Pro Monthly",
                # interval=BillingInterval.MONTH,
                included_credits=Credits(5000),
                price=Money(amount=Decimal("299.00"), currency=Currency.USD),
            ),
            PlanCode("sub_enterprise_monthly"): SubscriptionPlan(
                code=PlanCode("sub_enterprise_monthly"),
                name="Enterprise Monthly",
                # interval=BillingInterval.MONTH,
                included_credits=Credits(20000),
                price=Money(amount=Decimal("999.00"), currency=Currency.USD),
            ),
        }

    async def get_subscription_plan(
        self, plan_code: PlanCode
    ) -> SubscriptionPlan | None:
        plan = self._plans.get(plan_code)
        if not plan:
            raise PricingNotFound(f"Subscription plan with code {plan_code} not found.")

        return plan
