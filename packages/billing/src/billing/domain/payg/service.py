from dataclasses import dataclass
from datetime import datetime, timedelta

from billing.domain.config import PAYG_EXPIRY_DAYS
from billing.domain.credits.models import CreditGrant
from billing.domain.errors import IdempotencyConflict
from billing.domain.events import BillingEvent
from billing.domain.payg.plans import (
    PaygPlan,
    get_payg_plan,
)
from billing.domain.types import (
    PlanCode,
    RequestId,
    UserId,
    utc_now,
)
from billing.domain.wallet.models import Wallet
from billing.domain.wallet.service import build_wallet


@dataclass(frozen=True)
class GrantPaygCreditsResult:
    grant: CreditGrant
    plan: PaygPlan
    wallet: Wallet
    event: BillingEvent


def grant_payg_credits(
    user_id: UserId,
    grants: list[CreditGrant],
    plan_code: PlanCode,
    request_id: RequestId | None = None,
    used_request_ids: set[str] | None = None,
    now: datetime | None = None,
) -> GrantPaygCreditsResult:
    now = now or utc_now()

    if (
        request_id is not None
        and used_request_ids is not None
        and str(request_id) in used_request_ids
    ):
        raise IdempotencyConflict(
            f"Request {request_id} already processed"
        )

    plan = get_payg_plan(plan_code)

    # Grant the credits
    grant = CreditGrant(
        # TODO: Need a proper strategy for generating grant IDs
        grant_id=...,
        user_id=user_id,
        source="payg",
        granted_credits=plan.credits_grant,
        remaining_credits=plan.credits_grant,
        created_at=now,
        expires_at=now + timedelta(days=PAYG_EXPIRY_DAYS),
        request_id=request_id,
        plan_code=plan.code,
    )
    grants.append(grant)

    # Mark request ID as used
    if (
        request_id is not None
        and used_request_ids is not None
    ):
        used_request_ids.add(str(request_id))

    # Build the wallet
    wallet = build_wallet(
        user_id=user_id,
        grants=grants,
        now=now,
    )

    event = BillingEvent(
        event_type="payg_credits_granted",
        user_id=wallet.user_id,
        credits=plan.credits_grant,
        plan_code=plan.code,
        request_id=request_id,
    )

    return GrantPaygCreditsResult(
        grant=grant,
        wallet=wallet,
        plan=plan,
        event=event,
    )
