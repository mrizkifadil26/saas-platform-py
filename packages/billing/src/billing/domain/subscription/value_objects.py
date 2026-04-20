from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from uuid import UUID, uuid4

SubscriptionStatus = Literal[
    "active",
    "past_due",
    "canceled",
]


@dataclass(frozen=True, slots=True)
class SubscriptionId:
    value: UUID

    @classmethod
    def generate(cls) -> SubscriptionId:
        return cls(uuid4())

    def __str__(self) -> str:
        return str(self.value)
