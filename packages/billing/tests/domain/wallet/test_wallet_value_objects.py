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

    assert wallet.user_id == user_id
    assert wallet.total_credits == Credits(150)
    assert wallet.subscription_credits == Credits(100)
    assert wallet.payg_credits == Credits(50)


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

    assert summary.user_id == user_id
    assert summary.total_credits == Credits(150)
    assert summary.subscription_credits == Credits(100)
    assert summary.payg_credits == Credits(50)
    assert summary.subscription_status == "active"
    assert (
        summary.subscription_plan_code == "sub_pro_monthly"
    )
    assert summary.current_period_end == now
