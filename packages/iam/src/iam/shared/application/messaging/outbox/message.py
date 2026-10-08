from dataclasses import dataclass
from datetime import datetime
from typing import Any

from iam.shared.application.messaging.message import MessageEnvelope


@dataclass(frozen=True, slots=True)
class OutboxMessage:
    message: MessageEnvelope[Any]
    attempts: int
    available_at: datetime
