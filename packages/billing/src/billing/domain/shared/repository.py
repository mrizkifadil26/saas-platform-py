from abc import ABC, abstractmethod
from typing import Generic, TypeVar

EntityT = TypeVar("EntityT")
IdT = TypeVar("IdT")


class Repository(ABC, Generic[EntityT, IdT]):
    @abstractmethod
    def get(self, entity_id: IdT) -> EntityT | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, entity: EntityT) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity: EntityT) -> None:
        raise NotImplementedError
