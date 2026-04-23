from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from billing.shared.domain.value_objects.currency import Currency

ZERO = Decimal("0")


def _to_decimal(value: Decimal | int | str) -> Decimal:
    if isinstance(value, Decimal):
        return value

    return Decimal(str(value))


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: Currency

    def __post_init__(self):
        amount = _to_decimal(self.amount)
        quantized_amount = amount.quantize(self._quantizer(), rounding=ROUND_HALF_UP)
        object.__setattr__(self, "amount", quantized_amount)

    def _quantizer(self) -> Decimal:
        if self.currency.minor_units == 0:
            return Decimal("1")

        return Decimal("1").scaleb(-self.currency.minor_units)

    @classmethod
    def zero(cls, currency: Currency) -> Money:
        return cls(
            amount=Decimal("0"),
            currency=currency,
        )

    @classmethod
    def from_minor(
        cls,
        minor_amount: int,
        currency: Currency,
    ) -> Money:
        divisor = Decimal("10") ** currency.minor_units
        return cls(
            amount=Decimal(minor_amount) / divisor,
            currency=currency,
        )

    @property
    def minor_amount(self) -> int:
        factor = Decimal("10") ** self.currency.minor_units
        return int((self.amount * factor).to_integral_value(rounding=ROUND_HALF_UP))

    def is_zero(self) -> bool:
        return self.amount == ZERO

    def is_positive(self) -> bool:
        return self.amount > ZERO

    def is_negative(self) -> bool:
        return self.amount < ZERO

    def assert_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(f"Currency mismatch: {self.currency} vs {other.currency}")

    def __add__(self, other: Money) -> Money:
        self.assert_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: Money) -> Money:
        self.assert_same_currency(other)
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def multiply(self, factor: Decimal | int | str) -> Money:
        factor_decimal = _to_decimal(factor)
        return Money(amount=self.amount * factor_decimal, currency=self.currency)

    def negate(self) -> Money:
        return Money(amount=-self.amount, currency=self.currency)

    def abs(self) -> Money:
        return Money(amount=abs(self.amount), currency=self.currency)

    def __lt__(self, other: Money) -> bool:
        self.assert_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: Money) -> bool:
        self.assert_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: Money) -> bool:
        self.assert_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: Money) -> bool:
        self.assert_same_currency(other)
        return self.amount >= other.amount

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
