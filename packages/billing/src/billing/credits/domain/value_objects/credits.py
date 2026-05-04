from __future__ import annotations

from dataclasses import dataclass

from billing.credits.domain.exceptions import (
    InsufficientCreditsError,
    InvalidCreditsAmountError,
)


@dataclass(frozen=True, slots=True, order=True)
class Credits:
    amount: int

    def __post_init__(self) -> None:
        if isinstance(self.amount, bool) or not isinstance(self.amount, int):
            raise InvalidCreditsAmountError("Credits amount must be an integer")

        if self.amount < 0:
            raise InvalidCreditsAmountError("Credits cannot be negative")

    @classmethod
    def zero(cls) -> Credits:
        return cls(0)

    @classmethod
    def of(cls, amount: int) -> Credits:
        return cls(amount)

    def is_zero(self) -> bool:
        return self.amount == 0

    def is_positive(self) -> bool:
        return self.amount > 0

    def can_cover(self, other: Credits) -> bool:
        return self.amount >= other.amount

    def min_with(self, other: Credits) -> Credits:
        return Credits(min(self.amount, other.amount))

    def __add__(self, other: Credits) -> Credits:
        if not isinstance(other, Credits):
            return NotImplemented

        return Credits(self.amount + other.amount)

    def __sub__(self, other: Credits) -> Credits:
        if not isinstance(other, Credits):
            return NotImplemented

        if other.amount > self.amount:
            raise InsufficientCreditsError(
                requested=other.amount,
                available=self.amount,
            )

        return Credits(self.amount - other.amount)

    def __int__(self) -> int:
        return self.amount

    def __str__(self) -> str:
        return str(self.amount)
