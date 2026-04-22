from dataclasses import dataclass
from datetime import datetime

from billing.domain.credits.value_objects import Credits
from billing.domain.shared.enums import BillingInterval
from billing.domain.shared.value_objects import PlanCode


@dataclass(frozen=True, slots=True)
class SubscriptionPlan:
    code: PlanCode
    name: str
    interval: BillingInterval
    price: Money
    included_credits: Credits

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise DomainInvariantError(
                "plan name cannot be blank"
            )
        if int(self.included_credits) < 0:
            raise DomainInvariantError(
                "included credits cannot be negative"
            )


@dataclass(frozen=True, slots=True)
class PaygPack:
    code: PackCode
    name: str
    price: Money
    credits: Credits
    expires_in_days: int

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise DomainInvariantError(
                "pack name cannot be blank"
            )
        if int(self.credits) <= 0:
            raise DomainInvariantError(
                "pack credits must be positive"
            )
        if self.expires_in_days <= 0:
            raise DomainInvariantError(
                "expires_in_days must be positive"
            )


@dataclass(frozen=True, slots=True)
class UsagePriceRule:
    product_code: ProductCode
    credits_per_unit: Credits
    effective_from: datetime
    effective_to: datetime | None = None

    def calculate_cost(self, quantity: int) -> Credits:
        if quantity < 0:
            raise DomainInvariantError(
                "quantity cannot be negative"
            )
        return Credits(
            int(self.credits_per_unit) * quantity
        )

    def is_effective_at(self, at: datetime) -> bool:
        if at < self.effective_from:
            return False
        if (
            self.effective_to is not None
            and at >= self.effective_to
        ):
            return False
        return True
