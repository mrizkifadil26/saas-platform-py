from dataclasses import dataclass
from datetime import datetime, timedelta

from packages.billing.src.billing.domain.config import (
    PAYG_EXPIRY_DAYS,
)
from packages.billing.src.billing.domain.credits.value_objects import (
    GrantId,
)
from packages.billing.src.billing.domain.payg.catalogs import (
    PaygPack,
    get_payg_pack,
)
from packages.billing.src.billing.domain.payg.entities import (
    PaygPurchase,
)
from packages.billing.src.billing.domain.payg.events import (
    PaygCreditsGranted,
)
from packages.billing.src.billing.domain.payg.value_objects import (
    PaygPurchaseId,
)
from packages.billing.src.billing.domain.shared.ids import (
    RequestId,
    UserId,
)
from packages.billing.src.billing.domain.shared.value_objects import (
    PlanCode,
)

from billing.domain.credits.entities import CreditGrant


@dataclass(frozen=True)
class CreatePaygPurchaseResult:
    purchase: PaygPurchase
    grant: CreditGrant
    pack: PaygPack
    event: PaygCreditsGranted


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
    # now = now or utc_now()

    # if (
    #     request_id is not None
    #     and used_request_ids is not None
    #     and str(request_id) in used_request_ids
    # ):
    #     raise IdempotencyConflict(
    #         f"Request {request_id} already processed"
    #     )

    pack = get_payg_pack(plan_code)

    clean_metadata = dict(metadata or {})

    purchase = PaygPurchase(
        purchase_id=purchase_id,
        user_id=user_id,
        plan_code=plan_code,
        credits=pack.credits,
        created_at=now,
        request_id=request_id,
        metadata=clean_metadata,
    )

    expires_at = now + timedelta(days=PAYG_EXPIRY_DAYS)

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
        },
    )

    # Mark request ID as used
    # if (
    #     request_id is not None
    #     and used_request_ids is not None
    # ):
    #     used_request_ids.add(str(request_id))

    # Build the wallet
    # wallet = build_wallet(
    #     user_id=user_id,
    #     grants=grants,
    #     now=now,
    # )

    # event = BillingEvent(
    #     event_type="payg_credits_granted",
    #     user_id=wallet.user_id,
    #     credits=plan.credits_grant,
    #     plan_code=plan.code,
    #     request_id=request_id,
    # )
    event = PaygCreditsGranted(
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
        event=event,
    )
