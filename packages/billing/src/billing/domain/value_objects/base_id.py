from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, order=True)
class BaseId:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError(f"{self.__class__.__name__} must be a string")

        value = self.value.strip()
        if not value:
            raise ValueError(f"{self.__class__.__name__} cannot be empty")

        try:
            UUID(value)
        except ValueError as exc:
            raise ValueError(f"{self.__class__.__name__} must be a valid UUID") from exc

        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        return self.value
