from collections.abc import Awaitable, Callable
from typing import Protocol, TypeVar


class Command:
    """Marker base class for commands."""


TCommand = TypeVar("TCommand", bound=Command, contravariant=True)
TResult = TypeVar("TResult", covariant=True)


class CommandHandler(Protocol[TCommand, TResult]):
    async def __call__(
        self,
        command: TCommand,
    ) -> TResult: ...


MiddlewareHandler = Callable[[Command], Awaitable[object]]


class CommandMiddleware(Protocol):
    async def __call__(
        self,
        command: Command,
        next: MiddlewareHandler,
    ) -> object: ...
