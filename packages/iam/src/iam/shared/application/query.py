from typing import Generic, Protocol, TypeVar

QueryResult = TypeVar("QueryResult")


class Query:
    pass


class QueryHandler(Protocol, Generic[QueryResult]):
    async def handle(self, query: Query) -> QueryResult:
        raise NotImplementedError
