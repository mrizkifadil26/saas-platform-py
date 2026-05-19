from dataclasses import dataclass

from iam.identity.domain.value_objects import UserId


@dataclass(frozen=True, slots=True)
class AccessTokenPayload:
    user_id: UserId
    permissions: frozenset[str]
