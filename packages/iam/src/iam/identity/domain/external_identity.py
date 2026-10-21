from dataclasses import dataclass
from datetime import datetime

from iam.accounts.domain.value_objects import UserId
from iam.identity.domain.enums import IdentityProvider
from iam.identity.domain.value_objects import ExternalIdentityId, ProviderSubject
from iam.shared.domain.email import EmailAddress
from iam.shared.kernel.entity import Entity


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
