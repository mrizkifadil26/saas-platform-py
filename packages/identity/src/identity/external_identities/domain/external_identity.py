from dataclasses import dataclass
from datetime import datetime

from identity.accounts.domain.value_objects import UserId
from identity.identity.domain.enums import IdentityProvider
from identity.identity.domain.value_objects import ExternalIdentityId, ProviderSubject
from identity.shared.domain.email import EmailAddress
from identity.shared.kernel.entity import Entity


@dataclass(slots=True)
class ExternalIdentity(Entity[ExternalIdentityId]):
    user_id: UserId

    provider: IdentityProvider
    subject: ProviderSubject

    email: EmailAddress
    email_verified: bool

    name: str | None

    created_at: datetime
    updated_at: datetime
