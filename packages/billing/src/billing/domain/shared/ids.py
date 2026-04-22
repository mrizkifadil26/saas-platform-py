from dataclasses import dataclass
from typing import NewType
from uuid import UUID

ReferenceId = NewType("ReferenceId", str)


class UserId:
    value: UUID | str

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class RequestId:
    value: str

    def __post_init__(self):
        normalized_value = self.value.strip()
        if not normalized_value:
            raise ValueError("RequestId cannot be empty")

        object.__setattr__(self, "value", normalized_value)

    def __str__(self) -> str:
        return self.value
