from typing import Any, Type

from iam.shared.application.command import Command


class CommandBus:
    def __init__(self) -> None:
        self._handlers: dict[Type[Command], Any] = {}

    def register(self, command_type: Type[Command], handler: Any) -> None:
        self._handlers[command_type] = handler

    async def dispatch(self, command: Command) -> Any:
        handler = self._handlers.get(type(command))

        if handler is None:
            raise RuntimeError(f"No command handler registered for {type(command).__name__}")

        return await handler.handle(command)
