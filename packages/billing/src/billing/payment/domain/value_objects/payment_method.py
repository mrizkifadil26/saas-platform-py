from dataclasses import dataclass
from enum import StrEnum


class PaymentMethodType(StrEnum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"
    MANUAL = "manual"


@dataclass(frozen=True, slots=True)
class PaymentMethod:
    type: PaymentMethodType
    provider: str | None = None
    reference: str | None = None
