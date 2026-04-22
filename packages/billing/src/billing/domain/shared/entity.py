from abc import ABC
from typing import Generic, TypeVar

IdT = TypeVar("IdT")


class Entity(ABC, Generic[IdT]):
    def __init__(self, id: IdT) -> None:
        self._id = id

    @property
    def id(self) -> IdT:
        return self._id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented

        return self.__class__ is other.__class__ and self.id == other.id

    def __hash__(self) -> int:
        return hash((self.__class__, self.id))
