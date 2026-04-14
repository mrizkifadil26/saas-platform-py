from dataclasses import dataclass

from billing.domain.types import Credits, UserId


@dataclass(frozen=True)
class Wallet:
    user_id: UserId
    total_credits: Credits
    subscription_credits: Credits
    payg_credits: Credits
