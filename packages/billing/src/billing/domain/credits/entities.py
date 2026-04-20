from dataclasses import dataclass, field
from datetime import datetime

from billing.domain.credits.exceptions import (
    InvalidCreditsAmount,
)
from billing.domain.credits.value_objects import (
    ConsumptionAllocation,
    ConsumptionId,
    Credits,
    GrantId,
)
from billing.domain.shared.enums import CreditSource
from billing.domain.shared.ids import RequestId, UserId
from billing.domain.shared.value_objects import (
    PlanCode,
)


@dataclass(eq=True, slots=True)
class CreditGrant:
    grant_id: GrantId
    user_id: UserId
    source: CreditSource
    granted_credits: Credits
    remaining_credits: Credits
    created_at: datetime
    expires_at: datetime | None = None
    request_id: RequestId | None = None
    plan_code: PlanCode | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def is_expired(self, now: datetime) -> bool:
        return (
            self.expires_at is not None
            and self.expires_at < now
        )

    def is_depleted(self) -> bool:
        return self.remaining_credits.is_zero()

    def is_active(self, now: datetime) -> bool:
        return (
            not self.is_expired(now)
            and not self.is_depleted()
        )

    def consume(
        self, amount: Credits
    ) -> ConsumptionAllocation:
        if int(amount) <= 0:
            raise InvalidCreditsAmount(
                f"Consumed credits must be positive, got {amount}"
            )

        if int(amount) > int(self.remaining_credits):
            raise InvalidCreditsAmount(
                f"Cannot consume more credits than remaining, got {amount}, remaining: {self.remaining_credits}"
            )

        self.remaining_credits = (
            self.remaining_credits - amount
        )

        return ConsumptionAllocation(
            grant_id=self.grant_id,
            credits=amount,
        )


@dataclass(eq=True, slots=True)
class CreditConsumption:
    consumption_id: ConsumptionId
    user_id: UserId
    cost: Credits
    created_at: datetime
    allocations: tuple[ConsumptionAllocation, ...]
    request_id: RequestId | None = None
    metadata: dict[str, str] = field(default_factory=dict)
