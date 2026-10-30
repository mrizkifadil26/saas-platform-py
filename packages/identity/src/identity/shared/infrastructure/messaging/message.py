from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID

# T = TypeVar("T")


# @dataclass(frozen=True, slots=True)
# class MessageMetadata:
#     message_id: UUID
#     occurred_at: datetime

# correlation_id: UUID | None = None
# causation_id: UUID | None = None

# schema_version: int = 1
# headers: dict[str, str] = field(default_factory=lambda: dict[str, str]())

# @classmethod
# def create(
#     cls,
# *,
# correlation_id: UUID | None = None,
# causation_id: UUID | None = None,
# schema_version: int = 1,
# headers: dict[str, str] | None = None,
# ) -> MessageMetadata:
#     return cls(
#         message_id=uuid4(),
# occurred_at=datetime.now(UTC),
# correlation_id=correlation_id,
# causation_id=causation_id,
# schema_version=schema_version,
# headers=headers or {},
# )


# @dataclass(frozen=True, slots=True)
# class MessageEnvelope(Generic[T]):
#     message_type: str
#     payload: T
#     metadata: MessageMetadata


@dataclass(frozen=True, slots=True)
class Message:
    id: UUID
    type: str
    payload: Mapping[str, Any]


class MessageDelivery(Protocol):
    async def ack(self) -> None: ...

    async def reject(
        self,
        *,
        requeue: bool = False,
    ) -> None: ...


@dataclass(slots=True)
class ReceivedMessage:
    message: Message
    delivery: MessageDelivery

    async def ack(self) -> None:
        await self.delivery.ack()

    async def reject(
        self,
        *,
        requeue: bool = False,
    ) -> None:
        await self.delivery.reject(requeue=requeue)
