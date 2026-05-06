from dataclasses import dataclass

from iam.identity.domain.value_objects.user_id import UserId
from iam.shared.application.query import Query


@dataclass(frozen=True, slots=True)
class GetUserById(Query):
    user_id: UserId


@dataclass(frozen=True, slots=True)
class GetUserByEmail(Query):
    email: str


@dataclass(frozen=True, slots=True)
class ListUsers(Query):
    limit: int = 50
    offset: int = 0
