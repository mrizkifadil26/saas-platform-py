from dataclasses import dataclass
from typing import Generic, TypeVar

EntityId = TypeVar("EntityId")


@dataclass(eq=False)
class Entity(Generic[EntityId]):
    """Base class for entities."""

    id: EntityId

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))
