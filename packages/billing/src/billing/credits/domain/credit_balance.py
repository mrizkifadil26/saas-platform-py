from __future__ import annotations

from dataclasses import dataclass, replace

from billing.credits.domain.exceptions import (
    InsufficientCreditsError,
    InsufficientReservedCreditsError,
    InvalidCreditsAmountError,
)
from billing.credits.domain.value_objects.credits import Credits


@dataclass(frozen=True, slots=True)
class CreditBalance:
    available: Credits
    reserved: Credits

    def __post_init__(self) -> None:
        if not isinstance(self.available, Credits):
            raise TypeError("available must be Credits")

        if not isinstance(self.reserved, Credits):
            raise TypeError("reserved must be Credits")

    @classmethod
    def zero(cls) -> CreditBalance:
        return cls(
            available=Credits.zero(),
            reserved=Credits.zero(),
        )

    @property
    def total(self) -> Credits:
        return self.available + self.reserved

    def can_reserve(self, amount: Credits) -> bool:
        return amount.is_positive() and self.available >= amount

    def can_consume_reserved(self, amount: Credits) -> bool:
        return amount.is_positive() and self.reserved >= amount

    def reserve(self, amount: Credits) -> CreditBalance:
        if amount.is_zero():
            raise InvalidCreditsAmountError(
                "Amount to reserve must be greater than zero"
            )

        if amount > self.available:
            raise InsufficientCreditsError(
                requested=int(amount),
                available=int(self.available),
            )

        return replace(
            self,
            available=self.available - amount,
            reserved=self.reserved + amount,
        )

    def release_reserved(self, amount: Credits) -> CreditBalance:
        if amount.is_zero():
            raise InvalidCreditsAmountError(
                "Amount to release cannot be zero or negative"
            )

        if amount > self.reserved:
            raise InsufficientReservedCreditsError(
                requested=int(amount),
                reserved=int(self.reserved),
            )

        return replace(
            self,
            available=self.available + amount,
            reserved=self.reserved - amount,
        )

    def consume_reserved(self, amount: Credits) -> CreditBalance:
        if amount.is_zero():
            raise InvalidCreditsAmountError(
                "Amount to consume cannot be zero or negative"
            )

        if amount > self.reserved:
            raise InsufficientReservedCreditsError(
                requested=int(amount),
                reserved=int(self.reserved),
            )

        return replace(
            self,
            reserved=self.reserved - amount,
        )

    def grant(self, amount: Credits) -> CreditBalance:
        if amount.is_zero():
            raise InvalidCreditsAmountError(
                "Amount to grant cannot be zero or negative"
            )

        return replace(
            self,
            available=self.available + amount,
        )

    def consume_available(self, amount: Credits) -> CreditBalance:
        if amount.is_zero():
            raise InvalidCreditsAmountError(
                "Amount to consume cannot be zero or negative"
            )

        if amount > self.available:
            raise InsufficientCreditsError(
                requested=int(amount),
                available=int(self.available),
            )

        return replace(
            self,
            available=self.available - amount,
        )
