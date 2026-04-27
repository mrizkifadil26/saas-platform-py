from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from billing.shared.domain.value_objects.currency import Currency


@dataclass(frozen=True, slots=True)
class Price:
    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        if self.amount < Decimal("0"):
            raise ValueError("Price amount cannot be negative")

        if not self.currency:
            raise ValueError("Currency is required")

        if len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter ISO code")

        object.__setattr__(self, "currency", self.currency.upper())

    @classmethod
    def zero(cls, currency: Currency) -> Price:
        return cls(amount=Decimal("0"), currency=currency)

    def is_zero(self) -> bool:
        return self.amount == Decimal("0")

    def multiply(self, quantity: int) -> Price:
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")

        return Price(
            amount=self.amount * Decimal(quantity),
            currency=self.currency,
        )
