from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from billing.domain.payg.exceptions import InvalidMoney


@dataclass(frozen=True, slots=True)
class PaygPurchaseId:
    value: UUID

    @classmethod
    def new(cls) -> PaygPurchaseId:
        return cls(uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class PackCode:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("PackCode cannot be blank")


class CreditGrantSource(StrEnum):
    PAYG = "payg"


TWOPLACES = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not self.currency.strip():
            raise InvalidMoney("currency cannot be blank")
        normalized = self.amount.quantize(
            TWOPLACES, rounding=ROUND_HALF_UP
        )
        object.__setattr__(self, "amount", normalized)

    @classmethod
    def zero(cls, currency: str) -> "Money":
        return cls(
            amount=Decimal("0.00"), currency=currency
        )

    def is_negative(self) -> bool:
        return self.amount < 0

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(
            amount=self.amount + other.amount,
            currency=self.currency,
        )

    def __sub__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(
            amount=self.amount - other.amount,
            currency=self.currency,
        )

    def __mul__(self, multiplier: int) -> "Money":
        return Money(
            amount=self.amount * Decimal(multiplier),
            currency=self.currency,
        )

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise InvalidMoney("currency mismatch")
