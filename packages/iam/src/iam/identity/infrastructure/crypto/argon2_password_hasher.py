from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerificationError, VerifyMismatchError

from iam.identity.application.interfaces import PasswordHasher


class Argon2PasswordHasher(PasswordHasher):
    def __init__(self) -> None:
        self._hasher = Argon2Hasher()

    def hash(self, raw_password: str) -> str:
        return self._hasher.hash(raw_password)

    def verify(
        self,
        raw_password: str,
        hashed_password: str,
    ) -> bool:
        try:
            return self._hasher.verify(
                hashed_password,
                raw_password,
            )
        except (VerifyMismatchError, VerificationError):
            return False
