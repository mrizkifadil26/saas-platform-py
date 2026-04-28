from __future__ import annotations

from dataclasses import dataclass

from billing.credits.domain.exceptions import InsufficientReservedCreditsError


@dataclass(frozen=True, slots=True)
class CreditBalance:
    available: int
    reserved: int = 0

    def __post_init__(self):
        if self.available < 0:
            raise ValueError("Available credit balance cannot be negative")
        if self.reserved < 0:
            raise ValueError("Reserved credit balance cannot be negative")

    @property
    def total(self) -> int:
        return self.available + self.reserved

    def reserve(self, amount: int) -> CreditBalance:
        if amount < 0:
            raise ValueError("Amount to reserve cannot be negative")

        if amount > self.available:
            raise ValueError("Cannot reserve more than available balance")

        return CreditBalance(
            available=self.available - amount,
            reserved=self.reserved + amount,
        )

    def consume_reserved(self, amount: int) -> CreditBalance:
        if amount <= 0:
            raise ValueError("Amount to consume cannot be zero or negative")

        if amount > self.reserved:
            raise ValueError("Cannot consume more than reserved balance")

        return CreditBalance(
            available=self.available + amount,
            reserved=self.reserved - amount,
        )

    def release_reserved(self, amount: int) -> CreditBalance:
        if amount <= 0:
            raise ValueError("Amount to release cannot be zero or negative")

        if amount > self.reserved:
            raise InsufficientReservedCreditsError(
                requested=amount,
                reserved=self.reserved,
            )

        return CreditBalance(
            available=self.available + amount,
            reserved=self.reserved - amount,
        )

    def add(self, amount: int) -> CreditBalance:
        if amount < 0:
            raise ValueError("Amount to add cannot be negative")

        return CreditBalance(
            available=self.available + amount,
            reserved=self.reserved,
        )

    def substract_available(self, amount: int) -> CreditBalance:
        if amount < 0:
            raise ValueError("Amount to substract cannot be negative")

        if amount > self.available:
            raise ValueError("Cannot substract more than available balance")

        return CreditBalance(
            available=self.available - amount,
            reserved=self.reserved,
        )
