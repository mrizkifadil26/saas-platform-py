import json
from datetime import datetime
from typing import Any
from uuid import UUID

from iam.shared.application.messaging.message import MessageEnvelope, MessageMetadata
from iam.shared.application.messaging.serializer import MessageSerializer


class JSONMessageSerializer(MessageSerializer):
    def serialize(self, message: MessageEnvelope[Any]) -> bytes:
        payload: dict[str, Any] = {
            "message_type": message.message_type,
            "message_id": str(message.metadata.message_id),
            "occurred_at": message.metadata.occurred_at.isoformat(),
            "payload": message.payload,
        }

        return json.dumps(
            payload,
            default=self._default,
            separators=(",", ":"),
        ).encode("utf-8")

    def deserialize(self, data: bytes) -> MessageEnvelope[Any]:
        value: dict[str, Any] = json.loads(data)

        return MessageEnvelope(
            message_type=value["message_type"],
            payload=value["payload"],
            metadata=MessageMetadata(
                message_id=UUID(value["message_id"]),
                occurred_at=datetime.fromisoformat(
                    value["occurred_at"],
                ),
            ),
        )

    @staticmethod
    def _default(value: object) -> Any:
        if isinstance(value, UUID):
            return str(value)

        if isinstance(value, datetime):
            return value.isoformat()

        raise TypeError(
            f"Object of type {type(value).__name__} is not JSON serializable",
        )
