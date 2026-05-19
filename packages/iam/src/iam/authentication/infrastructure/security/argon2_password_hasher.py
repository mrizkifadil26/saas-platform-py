from argon2 import PasswordHasher as Argon2Hasher

from iam.authentication.domain import PasswordHasher
from iam.authentication.domain.value_objects import PasswordHash


class Argon2PasswordHasher(PasswordHasher):
    def __init__(self) -> None:
        self._hasher = Argon2Hasher()

    def hash(
        self,
        plain_password: str,
    ) -> PasswordHash:
        hashed_password = self._hasher.hash(plain_password)

        return PasswordHash(hashed_password)
