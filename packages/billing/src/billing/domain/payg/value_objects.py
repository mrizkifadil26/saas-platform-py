from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class PaygPurchaseId:
    value: UUID

    @classmethod
    def new(cls) -> PaygPurchaseId:
        return cls(uuid4())

    def __str__(self) -> str:
        return str(self.value)
