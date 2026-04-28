from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, order=True)
class Credits:
    amount: int

    def __post_init__(self) -> None:
        if isinstance(self.amount, bool) or not isinstance(self.amount, int):
            raise TypeError("Credits amount must be an integer")

        if self.amount < 0:
            raise ValueError("Credits cannot be negative")

    @classmethod
    def zero(cls) -> Credits:
        return cls(0)

    def is_zero(self) -> bool:
        return self.amount == 0

    def is_positive(self) -> bool:
        return self.amount > 0

    def __add__(self, other: Credits) -> Credits:
        return Credits(self.amount + other.amount)

    def __sub__(self, other: Credits) -> Credits:
        if other.amount > self.amount:
            raise ValueError(
                f"Insufficient credits: cannot subtract {other.amount} from {self.amount}"
            )

        return Credits(self.amount - other.amount)

    def min(self, other: Credits) -> Credits:
        return Credits(min(self.amount, other.amount))

    def __int__(self) -> int:
        return self.amount

    def __str__(self) -> str:
        return str(self.amount)
