from __future__ import annotations

from dataclasses import dataclass

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

    @classmethod
    def zero(cls) -> CreditBalance:
        return cls(
            available=Credits.zero(),
            reserved=Credits.zero(),
        )

    @property
    def total(self) -> Credits:
        return self.available + self.reserved

    def reserve(self, amount: Credits) -> CreditBalance:
        if amount < Credits.zero():
            raise InvalidCreditsAmountError("Amount to reserve cannot be negative")

        if amount > self.available:
            raise InsufficientCreditsError(
                requested=int(amount),
                available=int(self.available),
            )

        return CreditBalance(
            available=self.available - amount,
            reserved=self.reserved + amount,
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

        return CreditBalance(
            available=self.available + amount,
            reserved=self.reserved - amount,
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

        return CreditBalance(
            available=self.available + amount,
            reserved=self.reserved - amount,
        )

    def add(self, amount: Credits) -> CreditBalance:
        if amount.is_zero():
            raise InvalidCreditsAmountError("Amount to add cannot be zero or negative")

        return CreditBalance(
            available=self.available + amount,
            reserved=self.reserved,
        )

    def subtract_available(self, amount: Credits) -> CreditBalance:
        if amount.is_zero():
            raise InvalidCreditsAmountError(
                "Amount to subtract cannot be zero or negative"
            )

        if amount > self.available:
            raise InsufficientCreditsError(
                requested=int(amount),
                available=int(self.available),
            )

        return CreditBalance(
            available=self.available - amount,
            reserved=self.reserved,
        )
