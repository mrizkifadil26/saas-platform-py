from dataclasses import dataclass
from datetime import datetime

from billing.domain.credits.entities import (
    ConsumptionAllocation,
    CreditConsumption,
    CreditGrant,
)
from billing.domain.credits.events import CreditsConsumed
from billing.domain.credits.exceptions import (
    InsufficientCredits,
    InvalidCreditsAmount,
)
from billing.domain.credits.policies import (
    grant_priority,
)
from billing.domain.credits.value_objects import (
    ConsumptionId,
    Credits,
)
from billing.domain.shared.ids import RequestId, UserId


@dataclass(frozen=True)
class ConsumeCreditsResult:
    consumption: CreditConsumption
    touched_grants: tuple[CreditGrant, ...]
    event: CreditsConsumed


def consume_credits(
    *,
    consumption_id: ConsumptionId,
    user_id: UserId,
    grants: list[CreditGrant],
    cost: Credits,
    now: datetime,
    request_id: RequestId | None = None,
    metadata: dict[str, str] | None = None,
) -> ConsumeCreditsResult:
    if int(cost) < 0:
        raise InvalidCreditsAmount(
            f"cost must be >= 0, got {cost}"
        )

    clean_metadata = dict(metadata or {})

    active_grants = [
        grant
        for grant in grants
        if grant.user_id == user_id and grant.is_active(now)
    ]
    active_grants.sort(key=grant_priority)

    available = sum(
        int(grant.remaining_credits)
        for grant in active_grants
    )

    if available < int(cost):
        raise InsufficientCredits(
            f"Insufficient credits: available {available}, cost={int(cost)}"
        )

    remaining_to_consume = int(cost)
    allocations: list[ConsumptionAllocation] = []
    touched_grants: list[CreditGrant] = []

    for grant in active_grants:
        if remaining_to_consume == 0:
            break

        to_consume = min(
            int(grant.remaining_credits),
            remaining_to_consume,
        )

        if to_consume <= 0:
            continue

        allocation = grant.consume(Credits(to_consume))
        allocations.append(allocation)

        touched_grants.append(grant)
        remaining_to_consume -= to_consume

    consumption = CreditConsumption(
        consumption_id=consumption_id,
        user_id=user_id,
        cost=cost,
        created_at=now,
        allocations=tuple(allocations),
        request_id=request_id,
        metadata=clean_metadata,
    )

    event = CreditsConsumed(
        consumption_id=consumption_id,
        user_id=user_id,
        cost=cost,
        allocations=tuple(allocations),
        occurred_at=now,
        request_id=request_id,
        metadata=clean_metadata,
    )

    return ConsumeCreditsResult(
        consumption=consumption,
        touched_grants=tuple(touched_grants),
        event=event,
    )
