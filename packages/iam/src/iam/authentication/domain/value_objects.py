from __future__ import annotations

from dataclasses import dataclass

from iam.shared.kernel import EntityId


@dataclass(frozen=True, slots=True)
class AuthenticationAttemptId(EntityId):
    pass


@dataclass(frozen=True, slots=True)
class CredentialId(EntityId):
    pass
