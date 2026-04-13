from dataclasses import dataclass

from billing.events import BillingEvent
from billing.models import Wallet

from .errors import IdempotencyConflict, InsufficientCredits, InvalidCreditsAmount
from .types import Credits, RequestId


def charge_credits(
    current_credits: Credits,
    cost: Credits,
    request_id: RequestId | None = None,
    used_request_ids: set[str] | None = None,
) -> Credits:
    """
    Deduct credits for a billing operation.

    Args:
        current_credits: The user's current credit balance.
        cost: The number of credits to charge.
        request_id: Optional idempotency key to prevent duplicate charges.
        used_request_ids: Set of already used request IDs (for idempotency).

    Returns:
        The new credit balance after deduction.

    Raises:
        InsufficientCredits: If current_credits < cost.
        IdempotencyConflict: If request_id is provided and already used.
    """
    if int(cost) < 0:
        raise InvalidCreditsAmount(f"cost must be >= 0, got {cost}")

    if (
        request_id is not None
        and used_request_ids is not None
        and str(request_id) in used_request_ids
    ):
        raise IdempotencyConflict(f"Request {request_id} already processed")

    if current_credits < cost:
        raise InsufficientCredits(f"Insufficient credits: {current_credits} < {cost}")

    new_credits = Credits(current_credits - cost)

    if request_id is not None and used_request_ids is not None:
        used_request_ids.add(str(request_id))

    return new_credits


@dataclass(frozen=True)
class ConsumeCreditsResult:
    wallet: Wallet
    event: BillingEvent


def consume_credits(
    wallet: Wallet,
    cost: Credits,
    request_id: RequestId | None = None,
    used_request_ids: set[str] | None = None,
) -> ConsumeCreditsResult:
    new_balance = charge_credits(
        current_credits=wallet.credits,
        cost=cost,
        request_id=request_id,
        used_request_ids=used_request_ids,
    )

    updated_wallet = Wallet(
        user_id=wallet.user_id,
        credits=new_balance,
    )

    event = BillingEvent(
        event_type="credits_charged",
        user_id=wallet.user_id,
        credits=cost,
        request_id=request_id,
    )

    return ConsumeCreditsResult(
        wallet=updated_wallet,
        event=event,
    )
