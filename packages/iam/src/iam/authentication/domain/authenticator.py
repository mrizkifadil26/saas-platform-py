from __future__ import annotations

from dataclasses import dataclass

from .authentication_decision import AuthenticationDecision
from .credential import Credential
from .enums import AuthenticationDenialReason
from .interfaces import PasswordHasher


@dataclass(frozen=True)
class Authenticator:
    password_hasher: PasswordHasher

    def authenticate_with_password(
        self,
        *,
        credential: Credential,
        password: str,
    ) -> AuthenticationDecision:
        # Rule validation

        is_valid_password = self.password_hasher.verify(
            plain_password=password,
            password_hash=credential.secret_hash.value,
        )

        if not is_valid_password:
            return AuthenticationDecision.deny(
                AuthenticationDenialReason.INVALID_CREDENTIALS,
            )

        return AuthenticationDecision.allow()
