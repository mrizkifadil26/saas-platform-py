# tests/support/fakes/user_repository.py

from dataclasses import dataclass, field

from iam.identity.domain import User
from iam.identity.domain.repositories import UserRepository
from iam.identity.domain.value_objects import Email, UserId


@dataclass(slots=True)
class InMemoryUserRepository(UserRepository):
    users: dict[object, User] = field(
        default_factory=lambda: dict[object, User](),
    )

    async def save(
        self,
        user: User,
    ) -> None:
        self.users[user.id] = user

    async def find_by_id(
        self,
        user_id: UserId,
    ) -> User | None:
        return self.users.get(user_id)

    async def find_by_email(
        self,
        email: Email,
    ) -> User | None:
        return next(
            (user for user in self.users.values() if user.email == email),
            None,
        )

    async def list(
        self,
        *,
        limit: int,
        offset: int,
    ) -> tuple[list[User], int]:
        users = list(self.users.values())
        total = len(users)

        return (
            users[offset : offset + limit],
            total,
        )
