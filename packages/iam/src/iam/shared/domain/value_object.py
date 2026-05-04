from dataclasses import dataclass
from typing import Generic, Self, TypeVar
from uuid import UUID, uuid4

from iam.shared.domain.exceptions import ValidationError

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ValueObject:
    pass


@dataclass(frozen=True, slots=True)
class Identifier(ValueObject, Generic[T]):
    value: T


@dataclass(frozen=True, slots=True)
class UUIDIdentifier(Identifier[UUID]):
    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise ValidationError(f"{type(self).__name__} must be a UUID")

    @classmethod
    def new(cls) -> Self:
        return cls(uuid4())

    @classmethod
    def from_str(cls, value: str) -> Self:
        try:
            return cls(UUID(value))
        except ValueError as exc:
            raise ValidationError(f"Invalid {cls.__name__} format") from exc

    def __str__(self) -> str:
        return str(self.value)

    def to_primitive(self) -> str:
        return str(self.value)
