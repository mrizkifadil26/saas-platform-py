from dataclasses import dataclass
from datetime import datetime

from billing.domain.credits.models import CreditGrant
from billing.domain.credits.policies import is_grant_active
from billing.domain.subscription.models import Subscription
from billing.domain.wallet.models import Wallet

from ..types import Credits, UserId, utc_now


def build_wallet(
    user_id: UserId,
    grants: list[CreditGrant],
    now: datetime | None = None,
) -> Wallet:
    now = now or utc_now()

    subscription_total = 0
    payg_total = 0

    for grant in grants:
        if grant.user_id != user_id:
            continue

        if not is_grant_active(grant, now):
            continue

        if grant.source == "subscription":
            subscription_total += int(
                grant.remaining_credits
            )
        elif grant.source == "payg":
            payg_total += int(grant.remaining_credits)

    total = subscription_total + payg_total

    return Wallet(
        user_id=user_id,
        total_credits=Credits(total),
        subscription_credits=Credits(subscription_total),
        payg_credits=Credits(payg_total),
    )


@dataclass(frozen=True)
class BillingSummary:
    user_id: UserId
    total_credits: Credits
    subscription_credits: Credits
    payg_credits: Credits
    subscription_status: str | None
    subscription_plan_code: str | None
    current_period_end: datetime | None


def get_billing_summary(
    user_id: UserId,
    grants: list[CreditGrant],
    subscription: Subscription | None = None,
    now: datetime | None = None,
) -> BillingSummary:
    now = now or utc_now()
    wallet = build_wallet(
        user_id=user_id,
        grants=grants,
        now=now,
    )

    return BillingSummary(
        user_id=user_id,
        total_credits=wallet.total_credits,
        subscription_credits=wallet.subscription_credits,
        payg_credits=wallet.payg_credits,
        subscription_status=subscription.status
        if subscription
        else None,
        subscription_plan_code=str(subscription.plan_code)
        if subscription
        else None,
        current_period_end=subscription.current_period_end
        if subscription
        else None,
    )
