from abc import ABC, abstractmethod

from billing.payg.domain.value_objects.pack_code import PackCode
from billing.pricing.application.dto import PaygCreditPackage, SubscriptionPlan
from billing.subscription.domain.value_objects.plan_code import PlanCode


class SubscriptionPricingCatalog(ABC):
    """
    Read-side pricing dependency.

    Subscription application asks pricing:
    'What does plan X cost?'

    It does NOT trust frontend price. Ever.
    """

    @abstractmethod
    async def get_subscription_plan(
        self,
        plan_code: PlanCode,
    ) -> SubscriptionPlan | None:
        raise NotImplementedError


class PaygPricingCatalog(ABC):
    """
    Read-side pricing dependency.

    PAYG application asks pricing:
    'What does package X cost?'

    It does NOT trust frontend price. Ever.
    """

    @abstractmethod
    async def get_payg_package(
        self, package_code: PackCode
    ) -> PaygCreditPackage | None:
        raise NotImplementedError
