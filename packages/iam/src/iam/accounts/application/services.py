from dataclasses import dataclass
from datetime import datetime

from iam.accounts.domain import User
from iam.accounts.domain.value_objects import UserId
from iam.shared.domain.email import EmailAddress

from .ports import UserRepository


@dataclass(slots=True)
class AccountService:
    users: UserRepository

    async def create_user(
        self,
        *,
        email: EmailAddress,
        email_verified_at: datetime | None,
        created_at: datetime,
    ) -> UserId:
        user = User.create(
            email=email,
            email_verified_at=email_verified_at,
            created_at=created_at,
        )

        await self.users.add(user)

        return user.id
