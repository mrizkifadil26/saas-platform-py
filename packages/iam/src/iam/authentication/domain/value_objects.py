from __future__ import annotations

from dataclasses import dataclass

from iam.shared.domain import EntityId, ValueObject


@dataclass(frozen=True, slots=True)
class AuthenticationAttemptId(EntityId):
    pass


@dataclass(frozen=True, slots=True)
class AuthenticationTokens:
    access_token: AccessToken
    refresh_token: RefreshToken


@dataclass(frozen=True, slots=True)
class AccessToken(ValueObject[str]):
    value: str

    def __post_init__(self) -> None:
        value = self.value.strip()

        if not value:
            raise ValueError("Access token cannot be empty")

        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class RefreshToken(ValueObject[str]):
    value: str

    def __post_init__(self) -> None:
        value = self.value.strip()

        if not value:
            raise ValueError("Refresh token cannot be empty")

        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class CredentialId(EntityId):
    pass


@dataclass(frozen=True, slots=True)
class PasswordHash(ValueObject[str]):
    value: str

    def __post_init__(self) -> None:
        value = self.value.strip()

        if not value:
            raise ValueError("Password hash cannot be empty")

        if len(value) > 500:
            raise ValueError("Password hash is too long")

        object.__setattr__(self, "value", value)
