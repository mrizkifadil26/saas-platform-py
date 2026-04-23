from dataclasses import dataclass
from datetime import datetime

from billing.domain.credits.value_objects import Credits
from billing.domain.shared.ids import UserId


@dataclass(frozen=True, slots=True)
class Wallet:
    user_id: UserId
    total_credits: Credits
    subscription_credits: Credits
    payg_credits: Credits


@dataclass(frozen=True, slots=True)
class BillingSummary:
    user_id: UserId
    total_credits: Credits
    subscription_credits: Credits
    payg_credits: Credits
    subscription_status: str | None
    subscription_plan_code: str | None
    current_period_end: datetime | None
