from dataclasses import dataclass, field
from datetime import datetime

from billing.domain.types import (
    Credits,
    PlanCode,
    RequestId,
    SubscriptionId,
    UserId,
)


@dataclass(frozen=True)
class GrantPaygPurchaseCommand:
    user_id: UserId
    plan_code: PlanCode
    request_id: RequestId
    occurred_at: datetime | None = None
    metadata: dict[str, str] | None = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class GrantSubscriptionPeriodCreditsCommand:
    subscription_id: SubscriptionId
    request_id: RequestId
    occurred_at: datetime | None = None
    metadata: dict[str, str] | None = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class RenewSubscriptionCommand:
    subscription_id: SubscriptionId
    next_period_start: datetime
    next_period_end: datetime
    request_id: RequestId
    occurred_at: datetime | None = None
    metadata: dict[str, str] | None = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class WalletDTO:
    user_id: UserId
    total_credits: Credits
    subscription_credits: Credits
    payg_credits: Credits


@dataclass(frozen=True)
class BillingSummaryDTO:
    user_id: UserId
    total_credits: Credits
    subscription_credits: Credits
    payg_credits: Credits
    subscription_status: str | None
    subscription_plan_code: PlanCode | None
    subscription_period_end: datetime | None


@dataclass(frozen=True)
class ConsumeCreditsResultDTO:
    user_id: UserId
    total_credits: Credits
    subscription_credits: Credits
    payg_credits: Credits
    charged_credits: Credits
    allocations: tuple[dict[str, object], ...]
