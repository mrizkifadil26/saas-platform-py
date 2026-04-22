from datetime import timedelta

from billing.domain.credits.value_objects import Credits
from billing.domain.payg.aggregates import PaygPurchase
from billing.domain.payg.events import (
    PaygCreditGrantRequested,
)
from billing.domain.pricing.entities import PaygPack


def build_payg_credit_grant_requested(
    *,
    purchase: PaygPurchase,
    pack: PaygPack,
    request_id=None,
) -> PaygCreditGrantRequested:
    if purchase.paid_at is None:
        raise ValueError(
            "purchase must be paid before requesting credit grant"
        )
    expires_at = purchase.paid_at + timedelta(
        days=pack.expires_in_days
    )
    return PaygCreditGrantRequested(
        purchase_id=purchase.purchase_id,
        user_id=purchase.user_id,
        pack_code=purchase.pack_code,
        credits=Credits(int(pack.credits)),
        expires_at=expires_at,
        request_id=request_id,
    )
