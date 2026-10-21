from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import Generic, TypeVar


@dataclass(frozen=True, slots=True)
class ThrottleKey:
    namespace: str
    identifier: str

    def __post_init__(self) -> None:
        if not self.namespace:
            raise ValueError("namespace must not be empty")

        if not self.identifier:
            raise ValueError("identifier must not be empty")

    @property
    def value(self) -> str:
        return f"{self.namespace}:{self.identifier}"


TContext = TypeVar(
    "TContext",
    covariant=True,
)


@dataclass(frozen=True, slots=True)
class ThrottleRule(Generic[TContext]):
    namespace: str
    limit: int
    window: timedelta
    key: Callable[[TContext], str]

    def __post_init__(self) -> None:
        if self.limit <= 0:
            raise ValueError("limit must be greater than zero")

        if self.window <= timedelta(0):
            raise ValueError("window must be greater than zero")
