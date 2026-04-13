from dataclasses import dataclass

from billing.types import Credits, UserId


@dataclass(frozen=True)
class Wallet:
    user_id: UserId
    credits: Credits
