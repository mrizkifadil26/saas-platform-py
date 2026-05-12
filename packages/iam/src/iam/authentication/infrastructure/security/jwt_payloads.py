from dataclasses import dataclass

from iam.identity.domain.value_objects import UserId


@dataclass(frozen=True, slots=True)
class AccessTokenPayload:
    user_id: UserId
    permissions: frozenset[str]


# @dataclass(frozen=True, slots=True)
# class RefreshTokenPayload:
#     session_id: SessionId


@dataclass(frozen=True, slots=True)
class RegistrationTokenPayload:
    user_id: UserId
