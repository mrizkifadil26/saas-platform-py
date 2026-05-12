from dataclasses import dataclass
from typing import Generic, TypeVar, cast

IdT = TypeVar("IdT")


@dataclass(eq=False)
class Entity(Generic[IdT]):
    """Base class for entities."""

    id: IdT

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented

        other_entity = cast(Entity[IdT], other)

        return self.id == other_entity.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))
