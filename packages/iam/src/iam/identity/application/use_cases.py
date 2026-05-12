from datetime import UTC, datetime

from iam.identity.application.exceptions import UserAlreadyExistsError
from iam.identity.domain import User, UserRepository

from .commands import RegisterUserCommand


class RegisterUserUseCase:
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
        email = command.email

        existing_user = await self.user_repository.find_by_email(email)
        if existing_user is not None:
            raise UserAlreadyExistsError(email.value)

        user = User.register(
            email=email,
            registered_at=now,
        )

        await self.user_repository.save(user)
