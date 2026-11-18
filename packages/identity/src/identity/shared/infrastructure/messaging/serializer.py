from collections.abc import Mapping
from typing import Any, Protocol

# from .message import MessageEnvelope


class MessageSerializer(Protocol):
    def serialize(
        self,
        payload: Mapping[str, Any],
    ) -> bytes: ...

    def deserialize(
        self,
        payload: bytes,
    ) -> Mapping[str, Any]: ...
