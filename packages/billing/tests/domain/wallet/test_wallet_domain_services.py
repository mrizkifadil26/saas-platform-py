from datetime import timedelta

from billing.domain.credits.entities import CreditGrant
from billing.domain.credits.value_objects import (
    Credits,
    GrantId,
)
from billing.domain.shared.ids import UserId
from billing.domain.shared.value_objects import PlanCode
from billing.domain.subscription.entities import (
    Subscription,
)

from billing.domain.wallet.domain_services import (
    build_wallet,
    get_billing_summary,
)


def make_credit_grant(
    *,
    user_id,
    now,
    source,
    remaining_credits,
    expires_at=None,
):
    return CreditGrant(
        grant_id=GrantId.new(),
        user_id=user_id,
        source=source,
        granted_credits=remaining_credits,
        remaining_credits=remaining_credits,
        created_at=now,
        expires_at=expires_at,
        metadata={},
    )


def make_subscription(*, subscription_id, user_id, now):
    return Subscription(
        subscription_id=subscription_id,
        user_id=user_id,
        plan_code=PlanCode("sub_pro_monthly"),
        status="active",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        cancel_at_period_end=False,
    )


def test_build_wallet_returns_totals_for_active_subscription_and_payg_grants(
    now, user_id
):
    grants = [
        make_credit_grant(
            user_id=user_id,
            now=now,
            source="subscription",
            remaining_credits=Credits(100),
        ),
        make_credit_grant(
            user_id=user_id,
            now=now,
            source="payg",
            remaining_credits=Credits(50),
        ),
    ]

    wallet = build_wallet(
        user_id=user_id,
        grants=grants,
        now=now,
    )

    assert wallet.total_credits == Credits(150)
    assert wallet.subscription_credits == Credits(100)
    assert wallet.payg_credits == Credits(50)


def test_build_wallet_ignores_inactive_foreign_and_non_wallet_grants(
    now, user_id
):
    grants = [
        make_credit_grant(
            user_id=user_id,
            now=now,
            source="subscription",
            remaining_credits=Credits(100),
        ),
        make_credit_grant(
            user_id=user_id,
            now=now,
            source="payg",
            remaining_credits=Credits(50),
            expires_at=now - timedelta(seconds=1),
        ),
        make_credit_grant(
            user_id=UserId("other_user"),
            now=now,
            source="payg",
            remaining_credits=Credits(25),
        ),
        make_credit_grant(
            user_id=user_id,
            now=now,
            source="promotion",
            remaining_credits=Credits(75),
        ),
        make_credit_grant(
            user_id=user_id,
            now=now,
            source="compensation",
            remaining_credits=Credits(30),
        ),
    ]

    wallet = build_wallet(
        user_id=user_id,
        grants=grants,
        now=now,
    )

    assert wallet.total_credits == Credits(205)
    assert wallet.subscription_credits == Credits(100)
    assert wallet.payg_credits == Credits(0)


def test_get_billing_summary_returns_wallet_totals_and_subscription_snapshot(
    now, user_id, subscription_id
):
    grants = [
        make_credit_grant(
            user_id=user_id,
            now=now,
            source="subscription",
            remaining_credits=Credits(100),
        ),
        make_credit_grant(
            user_id=user_id,
            now=now,
            source="payg",
            remaining_credits=Credits(50),
        ),
    ]
    subscription = make_subscription(
        subscription_id=subscription_id,
        user_id=user_id,
        now=now,
    )

    summary = get_billing_summary(
        user_id=user_id,
        grants=grants,
        subscription=subscription,
        now=now,
    )

    assert summary.user_id == user_id
    assert summary.total_credits == Credits(150)
    assert summary.subscription_credits == Credits(100)
    assert summary.payg_credits == Credits(50)
    assert summary.subscription_status == "active"
    assert (
        summary.subscription_plan_code == "sub_pro_monthly"
    )
    assert summary.current_period_end == now + timedelta(
        days=30
    )


def test_get_billing_summary_returns_none_subscription_fields_without_subscription(
    now, user_id
):
    summary = get_billing_summary(
        user_id=user_id,
        grants=[],
        subscription=None,
        now=now,
    )

    assert summary.user_id == user_id
    assert summary.total_credits == Credits(0)
    assert summary.subscription_credits == Credits(0)
    assert summary.payg_credits == Credits(0)
    assert summary.subscription_status is None
    assert summary.subscription_plan_code is None
    assert summary.current_period_end is None


def test_get_billing_summary_ignores_subscription_for_other_user(
    now, user_id, subscription_id
):
    summary = get_billing_summary(
        user_id=user_id,
        grants=[],
        subscription=make_subscription(
            subscription_id=subscription_id,
            user_id=UserId("other_user"),
            now=now,
        ),
        now=now,
    )

    assert summary.user_id == user_id
    assert summary.subscription_status is None
    assert summary.subscription_plan_code is None
    assert summary.current_period_end is None
