from dataclasses import dataclass
from datetime import datetime, timedelta

from billing.domain.config import PAYG_EXPIRY_DAYS
from billing.domain.credits.entities import CreditGrant
from billing.domain.credits.value_objects import GrantId
from billing.domain.payg.catalogs import (
    PaygPack,
    get_payg_pack,
)
from billing.domain.payg.entities import PaygPurchase
from billing.domain.payg.events import PaygCreditsPurchased
from billing.domain.payg.value_objects import (
    CreditGrantSource,
    PaygPurchaseId,
)
from billing.domain.shared.ids import RequestId, UserId
from billing.domain.shared.value_objects import PlanCode


@dataclass(frozen=True)
class CreatePaygPurchaseResult:
    purchase: PaygPurchase
    grant: CreditGrant
    pack: PaygPack
    event: PaygCreditsPurchased


def create_payg_purchase(
    *,
    purchase_id: PaygPurchaseId,
    grant_id: GrantId,
    user_id: UserId,
    plan_code: PlanCode,
    now: datetime,
    request_id: RequestId | None = None,
    metadata: dict[str, str] | None = None,
) -> CreatePaygPurchaseResult:
    pack = get_payg_pack(plan_code)
    clean_metadata = dict(metadata or {})
    expires_at = now + timedelta(days=PAYG_EXPIRY_DAYS)

    purchase = PaygPurchase(
        purchase_id=purchase_id,
        user_id=user_id,
        plan_code=plan_code,
        credits=pack.credits,
        created_at=now,
        request_id=request_id,
        metadata=clean_metadata,
    )

    # Grant the credits
    grant = CreditGrant(
        grant_id=grant_id,
        user_id=user_id,
        source="payg",
        granted_credits=pack.credits,
        remaining_credits=pack.credits,
        created_at=now,
        expires_at=expires_at,
        request_id=request_id,
        plan_code=pack.code,
        metadata={
            **clean_metadata,
            "plan_code": str(pack.code),
            "purchase_id": str(purchase.purchase_id),
            "grant_source": CreditGrantSource.PAYG.value,
        },
    )

    purchase_event = PaygCreditsPurchased(
        purchase_id=str(purchase.purchase_id),
        user_id=user_id,
        plan_code=plan_code,
        credits=pack.credits,
        occurred_at=now,
        request_id=request_id,
        metadata=clean_metadata,
    )

    return CreatePaygPurchaseResult(
        purchase=purchase,
        grant=grant,
        pack=pack,
        event=purchase_event,
    )
