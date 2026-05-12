from dataclasses import dataclass
from datetime import UTC, datetime

from iam.identity.domain import (
    User,
    UserRepository,
)
from iam.identity.domain.value_objects import EmailAddress

from .exceptions import (
    UserAlreadyExistsError,
)


@dataclass(frozen=True, slots=True)
class RegisterUserCommand:
    email: str


class RegisterUserService:
    def __init__(
        self,
        user_repository: UserRepository,
    ):
        self.user_repository = user_repository

    async def execute(
        self,
        command: RegisterUserCommand,
    ) -> None:
        now = datetime.now(UTC)
        email = EmailAddress(command.email)

        existing_user = await self.user_repository.find_by_email(email)
        if existing_user is not None:
            raise UserAlreadyExistsError(command.email)

        user = User.register(
            email=email,
            registered_at=now,
        )

        await self.user_repository.save(user)
