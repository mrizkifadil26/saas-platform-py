from dataclasses import dataclass

from iam.authentication.application.commands import UUID
from iam.authentication.application.use_cases import UserId, UserRepository
from iam.identity.application.dto import GetUserResult
from iam.identity.application.exceptions import UserNotFoundError


@dataclass(frozen=True, slots=True)
class GetUserQuery:
    user_id: UUID


@dataclass(slots=True)
class GetUser:
    user_repository: UserRepository

    async def execute(
        self,
        query: GetUserQuery,
    ) -> GetUserResult:
        user_id = UserId(query.user_id)

        user = await self.user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        return GetUserResult(
            id=user.id.value,
            email=user.email.value,
            # name=user.name,
            email_verified=user.is_email_verified,
        )
