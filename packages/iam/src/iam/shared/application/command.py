from typing import Generic, Protocol, TypeVar

CommandResult = TypeVar("CommandResult")


class Command:
    pass


class CommandHandler(Protocol, Generic[CommandResult]):
    async def handle(self, command: Command) -> CommandResult:
        raise NotImplementedError
