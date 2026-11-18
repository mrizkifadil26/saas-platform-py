import json
from collections.abc import Mapping
from datetime import datetime
from typing import Any, cast
from uuid import UUID

from identity.shared.infrastructure.messaging.serializer import MessageSerializer


class JsonPayloadSerializer(MessageSerializer):
    def serialize(self, payload: Mapping[str, Any]) -> bytes:
        return json.dumps(
            payload,
            default=self._default,
            separators=(",", ":"),
        ).encode("utf-8")

    def deserialize(self, payload: bytes) -> Mapping[str, Any]:
        value = json.loads(payload)

        if not isinstance(value, dict):
            raise ValueError("Message payload must be a JSON object")

        return cast(dict[str, Any], value)

    @staticmethod
    def _default(value: object) -> Any:
        if isinstance(value, UUID):
            return str(value)

        if isinstance(value, datetime):
            return value.isoformat()

        raise TypeError(
            f"Object of type {type(value).__name__} is not JSON serializable",
        )
