from typing import Protocol, TypeVar

T = TypeVar("T")


class Serializer(Protocol[T]):
    def serialize(
        self,
        value: T,
    ) -> bytes: ...

    def deserialize(
        self,
        data: bytes,
        type_: type[T],
    ) -> T: ...
