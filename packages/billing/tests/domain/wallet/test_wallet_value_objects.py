from billing.domain.credits.value_objects import Credits
from billing.domain.wallet.value_objects import (
    BillingSummary,
    Wallet,
)


def test_wallet_preserves_totals(user_id):
    wallet = Wallet(
        user_id=user_id,
        total_credits=Credits(150),
        subscription_credits=Credits(100),
        payg_credits=Credits(50),
    )

    assert wallet == Wallet(
        user_id=user_id,
        total_credits=Credits(150),
        subscription_credits=Credits(100),
        payg_credits=Credits(50),
    )


def test_billing_summary_preserves_wallet_snapshot_fields(
    now, user_id
):
    summary = BillingSummary(
        user_id=user_id,
        total_credits=Credits(150),
        subscription_credits=Credits(100),
        payg_credits=Credits(50),
        subscription_status="active",
        subscription_plan_code="sub_pro_monthly",
        current_period_end=now,
    )

    assert summary == BillingSummary(
        user_id=user_id,
        total_credits=Credits(150),
        subscription_credits=Credits(100),
        payg_credits=Credits(50),
        subscription_status="active",
        subscription_plan_code="sub_pro_monthly",
        current_period_end=now,
    )
