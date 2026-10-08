from typing import Any, Protocol

from .message import MessageEnvelope


class MessageSerializer(Protocol):
    def serialize(self, message: MessageEnvelope[Any]) -> bytes: ...

    def deserialize(self, data: bytes) -> MessageEnvelope[Any]: ...
