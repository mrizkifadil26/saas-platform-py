from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar


@dataclass(frozen=True, slots=True)
class Query:
    pass


QueryType = TypeVar(
    "QueryType",
    bound=Query,
    contravariant=True,
)

QueryResult = TypeVar(
    "QueryResult",
    covariant=True,
)


class QueryHandler(Protocol, Generic[QueryType, QueryResult]):
    async def handle(self, query: QueryType) -> QueryResult: ...
