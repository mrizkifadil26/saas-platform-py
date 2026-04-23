from __future__ import annotations

from enum import StrEnum


class Currency(StrEnum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    SGD = "SGD"
    IDR = "IDR"

    @property
    def minor_units(self) -> int:
        if self in {
            Currency.USD,
            Currency.EUR,
            Currency.GBP,
            Currency.SGD,
        }:
            return 2

        if self == Currency.IDR:
            return 0

        raise ValueError(f"Unsupported currency: {self}")

    @classmethod
    def from_string(cls, value: str) -> Currency:
        try:
            return cls(value)
        except ValueError as exc:
            raise ValueError(f"Unsupported currency: {value}") from exc
