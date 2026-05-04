from typing import Any, Type

from iam.shared.application.query import Query


class QueryBus:
    def __init__(self) -> None:
        self._handlers: dict[Type[Query], Any] = {}

    def register(self, query_type: Type[Query], handler: Any) -> None:
        self._handlers[query_type] = handler

    async def ask(self, query: Query) -> Any:
        handler = self._handlers.get(type(query))

        if handler is None:
            raise RuntimeError(f"No query handler registered for {type(query).__name__}")

        return await handler.handle(query)
