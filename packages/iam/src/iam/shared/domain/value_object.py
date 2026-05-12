from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ValueObject(Generic[T]):
    value: T

    def unwrap(self) -> T:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"
