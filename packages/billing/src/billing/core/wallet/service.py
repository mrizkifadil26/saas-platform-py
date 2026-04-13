from dataclasses import dataclass

from billing.core.events import BillingEvent
from billing.core.models import Wallet

from ..errors import IdempotencyConflict, InsufficientCredits, InvalidCreditsAmount
from ..types import Credits, RequestId


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
    if int(cost) < 0:
        raise InvalidCreditsAmount(f"cost must be >= 0, got {cost}")

    if (
        request_id is not None
        and used_request_ids is not None
        and str(request_id) in used_request_ids
    ):
        raise IdempotencyConflict(f"Request {request_id} already processed")

    new_balance = Credits(wallet.credits - cost)

    if wallet.credits < cost:
        raise InsufficientCredits(f"Insufficient credits: {wallet.credits} < {cost}")

    if request_id is not None and used_request_ids is not None:
        used_request_ids.add(str(request_id))

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
