from dataclasses import dataclass

from iam.accounts.application.ports import UserRepository

from .dto import ExternalAuthentication
from .ports import ExternalIdentityRepository, IdentityProviderRegistry


@dataclass(slots=True)
class ExternalIdentityService:
    providers: IdentityProviderRegistry
    identities: ExternalIdentityRepository
    users: UserRepository

    async def authenticate(
        self,
        *,
        provider: str,
        authorizaton_code: str,
    ) -> ExternalAuthentication: ...
