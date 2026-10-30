from typing import Protocol


class CredentialVerifier(Protocol):
    async def verify(
        self,
        credential: Credential,
        secret: Secret,
    ) -> bool: ...


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
