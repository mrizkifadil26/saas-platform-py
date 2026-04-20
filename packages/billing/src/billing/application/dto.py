from dataclasses import dataclass, field
from datetime import datetime

from billing.domain.credits.value_objects import Credits
from billing.domain.shared.ids import RequestId, UserId
from billing.domain.shared.value_objects import PlanCode


@dataclass(frozen=True, slots=True)
class GrantPaygPurchaseCommand:
    user_id: UserId
    plan_code: PlanCode
    request_id: RequestId
    occurred_at: datetime | None = None
    metadata: dict[str, str] | None = field(
        default_factory=dict
    )


@dataclass(frozen=True, slots=True)
class ConsumeCreditsCommand:
    user_id: UserId
    cost: Credits
    request_id: RequestId | None = None
    occurred_at: datetime | None = None
    metadata: dict[str, str] | None = field(
        default_factory=dict
    )


@dataclass(frozen=True, slots=True)
class WalletDTO:
    user_id: UserId
    total_credits: Credits
    subscription_credits: Credits
    payg_credits: Credits


@dataclass(frozen=True, slots=True)
class BillingSummaryDTO:
    user_id: UserId
    total_credits: Credits
    subscription_credits: Credits
    payg_credits: Credits
    subscription_status: str | None
    subscription_plan_code: str | None
    subscription_period_end: datetime | None


@dataclass(frozen=True, slots=True)
class ConsumeCreditsResultDTO:
    user_id: UserId
    total_credits: Credits
    subscription_credits: Credits
    payg_credits: Credits
    charged_credits: Credits
    allocations: tuple[dict[str, object], ...]
