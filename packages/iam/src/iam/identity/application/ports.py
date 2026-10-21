from typing import Protocol

from iam.identity.application.dto import ExternalProfile
from iam.identity.domain import ExternalIdentity, IdentityProvider


class ExternalIdentityRepository(Protocol):
    async def get(
        self,
        *,
        provider: IdentityProvider,
        subject: str,
    ) -> ExternalIdentity | None: ...

    async def add(
        self,
        identity: ExternalIdentity,
    ) -> None: ...


class IdentityProviderClient(Protocol):
    name: IdentityProvider

    async def authenticate(
        self,
        *,
        authorization_code: str,
        redirect_uri: str,
    ) -> ExternalProfile: ...


class IdentityProviderRegistry(Protocol):
    def get(
        self,
        provider: IdentityProvider,
    ) -> IdentityProviderClient: ...
