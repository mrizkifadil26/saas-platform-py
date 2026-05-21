from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar
from uuid import UUID, uuid4

from .exceptions import ValidationError
from .value_object import ValueObject

EntityIdT = TypeVar(
    "EntityIdT",
    bound=EntityId,
)


@dataclass(frozen=True, slots=True)
class EntityId(ValueObject[UUID]):
    value: UUID

    @classmethod
    def generate(
        cls: type[EntityIdT],
    ) -> EntityIdT:
        return cls(uuid4())

    @classmethod
    def from_uuid(
        cls: type[EntityIdT],
        value: UUID,
    ) -> EntityIdT:
        return cls(value)

    @classmethod
    def from_string(
        cls: type[EntityIdT],
        value: str,
    ) -> EntityIdT:
        try:
            return cls(UUID(value))
        except ValueError as exc:
            raise ValidationError(
                f"Invalid {cls.__name__} format",
            ) from exc
