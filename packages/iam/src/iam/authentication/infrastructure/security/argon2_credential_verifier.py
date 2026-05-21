from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerificationError, VerifyMismatchError

from iam.authentication.application import CredentialVerifier
from iam.authentication.domain.value_objects import PasswordHash


class Argon2CredentialVerifier(CredentialVerifier):
    def __init__(self) -> None:
        self._hasher = Argon2Hasher()

    def verify_password(
        self,
        *,
        password: str,
        password_hash: PasswordHash,
    ) -> bool:

        try:
            return self._hasher.verify(
                password_hash.unwrap(),
                password,
            )
        except (VerifyMismatchError, VerificationError):
            return False
