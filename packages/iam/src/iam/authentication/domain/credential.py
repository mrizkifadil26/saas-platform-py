from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from iam.identity.domain.value_objects import UserId
from iam.shared.domain import Entity

from .enums import CredentialStatus
from .value_objects import CredentialId, PasswordHash


@dataclass(eq=False, slots=True)
class Credential(Entity[CredentialId]):
    user_id: UserId
    password_hash: PasswordHash
    status: CredentialStatus
    created_at: datetime
    updated_at: datetime | None

    @classmethod
    def create(
        cls,
        user_id: UserId,
        password_hash: PasswordHash,
        *,
        created_at: datetime,
    ) -> Credential:
        return cls(
            id=CredentialId.generate(),
            user_id=user_id,
            password_hash=password_hash,
            status=CredentialStatus.ACTIVE,
            created_at=created_at,
            updated_at=None,
        )

    def change_password(
        self,
        password_hash: PasswordHash,
        *,
        at: datetime,
    ) -> None:
        self.password_hash = password_hash
        self.updated_at = at

    def disable(
        self,
        *,
        at: datetime,
    ) -> None:
        if self.status is CredentialStatus.DISABLED:
            return

        self.status = CredentialStatus.DISABLED
        self.updated_at = at

    def mark_compromised(
        self,
        *,
        at: datetime,
    ) -> None:
        self.status = CredentialStatus.COMPROMISED
        self.updated_at = at

    def _ensure_active(self) -> None:
        if self.status is not CredentialStatus.ACTIVE:
            # TODO: raise invalid credentials
            # raise InvalidCredentials("Credential is not active")
            raise
