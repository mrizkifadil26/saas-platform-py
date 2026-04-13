from dataclasses import dataclass

from billing.errors import IdempotencyConflict
from billing.events import BillingEvent
from billing.models import Wallet
from billing.subscription.plans import SubscriptionPlan, get_subscription_plan
from billing.types import Credits, PlanCode, RequestId


@dataclass(frozen=True)
class GrantSubscriptionCreditsResult:
    wallet: Wallet
    plan: SubscriptionPlan
    event: BillingEvent


def grant_subscription_credits(
    wallet: Wallet,
    plan_code: PlanCode,
    request_id: RequestId | None = None,
    used_request_ids: set[str] | None = None,
) -> GrantSubscriptionCreditsResult:
    if (
        request_id is not None
        and used_request_ids is not None
        and str(request_id) in used_request_ids
    ):
        raise IdempotencyConflict(f"Request {request_id} already processed")

    plan = get_subscription_plan(plan_code)
    new_balance = Credits(wallet.credits + plan.credits_grant)

    if request_id is not None and used_request_ids is not None:
        used_request_ids.add(str(request_id))

    updated_wallet = Wallet(
        user_id=wallet.user_id,
        credits=new_balance,
    )

    event = BillingEvent(
        event_type="subscription_credits_granted",
        user_id=wallet.user_id,
        credits=plan.credits_grant,
        plan_code=plan.code,
        request_id=request_id,
    )

    return GrantSubscriptionCreditsResult(
        wallet=updated_wallet,
        plan=plan,
        event=event,
    )
