from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from billing.domain.credits.exceptions import (
    InvalidCreditsAmount,
)


@dataclass(frozen=True, slots=True)
class Credits:
    value: int

    def __post_init__(self):
        if self.value < 0:
            raise InvalidCreditsAmount(
                "Credits must be non-negative"
            )

    def __int__(self) -> int:
        return self.value

    def is_zero(self) -> bool:
        return self.value == 0

    def __add__(self, other: Credits) -> Credits:
        return Credits(self.value + other.value)

    def __sub__(self, other: Credits) -> Credits:
        result = self.value - other.value
        if result < 0:
            raise InvalidCreditsAmount(
                "Insufficient credits"
            )

        return Credits(result)

    def __str__(self) -> str:
        return str(self.value)


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
