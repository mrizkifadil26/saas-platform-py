from datetime import datetime
from typing import Any

from iam.authentication.domain import Credential, CredentialStatus, CredentialType
from iam.authentication.domain.value_objects import CredentialId, PasswordHash
from iam.identity.domain.value_objects import UserId
from tests.factories.identity import make_user_id
from tests.factories.shared import make_datetime


def make_credential(
    *,
    id: CredentialId | None = None,
    user_id: UserId | None = None,
    type: CredentialType = CredentialType.PASSWORD,
    secret_hash: PasswordHash | None = None,
    status: CredentialStatus = CredentialStatus.ACTIVE,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
    attributes: dict[str, Any] | None = None,
) -> Credential:
    return Credential(
        id=id or CredentialId.generate(),
        user_id=user_id or make_user_id(),
        type=type,
        secret_hash=secret_hash or PasswordHash("hashed-password"),
        status=status,
        created_at=created_at or make_datetime(),
        updated_at=updated_at,
        attributes=attributes if attributes is not None else {},
    )
