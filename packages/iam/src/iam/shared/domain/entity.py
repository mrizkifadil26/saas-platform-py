from dataclasses import dataclass
from typing import TypeVar


EntityId = TypeVar("EntityId")


@dataclass(eq=False)
class Entity:
    """Base class for entities."""

    id: EntityId

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))
