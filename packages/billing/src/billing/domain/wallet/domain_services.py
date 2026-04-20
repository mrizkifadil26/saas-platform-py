from datetime import datetime

from billing.domain.credits.entities import CreditGrant
from billing.domain.credits.value_objects import Credits
from billing.domain.shared.ids import UserId
from billing.domain.subscription.entities import (
    Subscription,
)
from billing.domain.wallet.value_objects import (
    BillingSummary,
    Wallet,
)


def build_wallet(
    *,
    user_id: UserId,
    grants: list[CreditGrant],
    # now: datetime | None = None,
    now: datetime,
) -> Wallet:
    # now = now or utc_now()

    subscription_total = 0
    payg_total = 0

    for grant in grants:
        if grant.user_id != user_id:
            continue

        if not grant.is_active(now):
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


def get_billing_summary(
    *,
    user_id: UserId,
    grants: list[CreditGrant],
    subscription: Subscription | None,
    now: datetime,
) -> BillingSummary:
    # now = now or utc_now()
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
