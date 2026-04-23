from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from billing.domain.credits.exceptions import (
    InvalidCreditsAmount,
)


@dataclass(frozen=True, slots=True)
class GrantId:
    value: UUID

    @classmethod
    def new(cls) -> GrantId:
        return cls(uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class ConsumptionId:
    value: UUID

    @classmethod
    def new(cls) -> ConsumptionId:
        return cls(uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class ConsumptionAllocation:
    grant_id: GrantId
    credits: Credits


@dataclass(frozen=True, slots=True)
class CreditBalance:
    amount: Credits

    def __post_init__(self):
        if self.amount.value < 0:
            raise InvalidCreditsAmount("Credit balance cannot be negative")


@dataclass(frozen=True, slots=True)
class CreditAccountId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("CreditAccountId cannot be blank")


@dataclass(frozen=True, slots=True)
class CreditGrantId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("CreditGrantId cannot be blank")


@dataclass(frozen=True, slots=True)
class CreditConsumptionId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("CreditConsumptionId cannot be blank")


@dataclass(frozen=True, slots=True)
class LedgerEntryId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("LedgerEntryId cannot be blank")


@dataclass(frozen=True, slots=True)
class ProductCode:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("ProductCode cannot be blank")
