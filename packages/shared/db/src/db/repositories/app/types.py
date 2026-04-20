from __future__ import annotations

from typing import Any, Protocol


class SupportsExecute(Protocol):
    async def execute(self, statement: Any, *args: Any, **kwargs: Any) -> Any: ...


class SupportsAdd(Protocol):
    def add(self, instance: Any) -> None: ...


class SupportsFlush(Protocol):
    async def flush(self) -> None: ...


class SupportsGet(Protocol):
    async def get(self, entity: Any, ident: Any, /, **kwargs: Any) -> Any: ...


class SupportsRepoSession(
    SupportsExecute,
    SupportsAdd,
    SupportsFlush,
    Protocol,
):
    pass


class SupportsFullRepoSession(
    SupportsExecute,
    SupportsAdd,
    SupportsFlush,
    SupportsGet,
    Protocol,
):
    pass
