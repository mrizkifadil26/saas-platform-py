from dataclasses import dataclass, field
from datetime import datetime

from billing.domain.types import (
    ConsumptionId,
    Credits,
    CreditSource,
    GrantId,
    PlanCode,
    RequestId,
    UserId,
)


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class ConsumptionAllocation:
    grant_id: GrantId
    credits: Credits


@dataclass(frozen=True)
class CreditConsumption:
    consumption_id: ConsumptionId
    user_id: UserId
    cost: Credits
    created_at: datetime
    request_id: RequestId | None = None
    allocations: tuple[ConsumptionAllocation, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)
