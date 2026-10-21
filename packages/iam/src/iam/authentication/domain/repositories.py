from typing import Protocol

from iam.accounts.domain.value_objects import UserId
from iam.authentication.domain import Credential, CredentialType
from iam.shared.domain.email import EmailAddress

# class AuthenticationAttemptRepository(Protocol):
#     async def save(
#         self,
#         attempt: AuthenticationAttempt,
#     ) -> None: ...

#     async def list_recent_by_user_id(
#         self,
#         user_id: UserId,
#         limit: int = 10,
#     ) -> list[AuthenticationAttempt]: ...

#     async def count_recent_failures(
#         self,
#         *,
#         email: Email,
#         since: datetime,
#     ) -> int: ...


class CredentialRepository(Protocol):
    async def save(
        self,
        credential: Credential,
    ) -> None: ...

    async def find_password_by_email(
        self,
        email: EmailAddress,
    ) -> Credential | None: ...

    async def find_by_user_and_type(
        self,
        user_id: UserId,
        credential_type: CredentialType,
    ) -> Credential | None: ...
