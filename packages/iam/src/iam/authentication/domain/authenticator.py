from __future__ import annotations

from dataclasses import dataclass

from .authentication_decision import AuthenticationDecision
from .credential import Credential
from .enums import AuthenticationDenialReason
from .interfaces import CredentialVerifier


@dataclass(frozen=True)
class Authenticator:
    verifier: CredentialVerifier

    def authenticate_with_password(
        self,
        *,
        credential: Credential,
        password: str,
    ) -> AuthenticationDecision:
        # Rule validation

        is_valid_password = self.verifier.verify_password(
            credential=credential,
            password=password,
        )

        if not is_valid_password:
            return AuthenticationDecision.deny(
                AuthenticationDenialReason.INVALID_CREDENTIALS,
            )

        return AuthenticationDecision.allow()
