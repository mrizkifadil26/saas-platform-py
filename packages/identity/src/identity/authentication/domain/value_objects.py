from __future__ import annotations

from dataclasses import dataclass

from identity.shared.kernel import EntityId


@dataclass(frozen=True, slots=True)
class AuthenticationAttemptId(EntityId):
    pass

