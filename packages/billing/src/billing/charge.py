from .errors import IdempotencyConflict, InsufficientCredits
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
    if request_id is not None and used_request_ids is not None and str(request_id) in used_request_ids:
        raise IdempotencyConflict(f"Request {request_id} already processed")

    if current_credits < cost:
        raise InsufficientCredits(f"Insufficient credits: {current_credits} < {cost}")

    new_credits = Credits(current_credits - cost)

    if request_id is not None and used_request_ids is not None:
        used_request_ids.add(str(request_id))

    return new_credits