from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar


@dataclass(frozen=True, slots=True)
class Command:
    pass


CommandType = TypeVar(
    "CommandType",
    bound=Command,
    contravariant=True,
)

CommandResult = TypeVar(
    "CommandResult",
    covariant=True,
)


class CommandHandler(Protocol, Generic[CommandType, CommandResult]):
    async def handle(self, command: CommandType) -> CommandResult: ...
