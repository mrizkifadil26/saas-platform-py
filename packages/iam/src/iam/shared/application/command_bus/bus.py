from collections.abc import Sequence
from typing import Any, cast

from .contracts import (
    Command,
    CommandHandler,
    CommandMiddleware,
    MiddlewareHandler,
    TCommand,
    TResult,
)
from .exceptions import CommandHandlerAlreadyRegistered, CommandHandlerNotFound

Handler = CommandHandler[Any, object]


class CommandBus:
    def __init__(
        self,
        middlewares: Sequence[CommandMiddleware] | None = None,
    ) -> None:
        self._handlers: dict[type[Command], Handler] = {}
        self._middlewares = tuple(middlewares or ())

    def register(
        self,
        command_type: type[TCommand],
        handler: CommandHandler[TCommand, TResult],
    ) -> None:
        if command_type in self._handlers:
            raise CommandHandlerAlreadyRegistered(command_type)

        self._handlers[command_type] = cast(Handler, handler)

    async def dispatch(self, command: Command) -> object:
        handler = self._handlers.get(type(command))

        if handler is None:
            raise CommandHandlerNotFound(type(command))

        async def invoke_handler(
            current: Command,
        ) -> object:
            return await handler(current)

        next_handler: MiddlewareHandler = invoke_handler
        for middleware in reversed(self._middlewares):
            next_handler = self._wrap(
                middleware,
                next_handler,
            )

        return await next_handler(command)
        # return cast(TResult, await handler(command))

    @staticmethod
    def _wrap(
        middleware: CommandMiddleware,
        next_handler: MiddlewareHandler,
    ) -> MiddlewareHandler:
        async def invoke(command: Command) -> object:
            return await middleware(command, next_handler)

        return invoke
