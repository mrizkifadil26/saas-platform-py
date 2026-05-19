from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerificationError, VerifyMismatchError

from iam.authentication.domain import Credential
from iam.authentication.domain.interfaces import CredentialVerifier


class Argon2CredentialVerifier(CredentialVerifier):
    def __init__(self) -> None:
        self._hasher = Argon2Hasher()

    def verify_password(
        self,
        *,
        credential: Credential,
        password: str,
    ) -> bool:
        secret_hash = credential.secret_hash
        try:
            return self._hasher.verify(
                secret_hash.value,
                password,
            )
        except (VerifyMismatchError, VerificationError):
            return False
