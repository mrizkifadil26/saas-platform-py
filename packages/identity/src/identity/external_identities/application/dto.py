from dataclasses import dataclass

from identity.accounts.domain.value_objects import UserId
from identity.identity.domain.enums import IdentityProvider
from identity.shared.domain.email import EmailAddress


@dataclass(frozen=True, slots=True)
class ExternalAuthentication:
    user_id: UserId
    provider: IdentityProvider
    is_new_identity: bool


@dataclass(frozen=True, slots=True)
class ExternalProfile:
    provider: IdentityProvider
    subject: str

    email: EmailAddress
    email_verified: bool

    name: str | None = None
