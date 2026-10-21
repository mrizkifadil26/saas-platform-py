from typing import Protocol

from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerificationError, VerifyMismatchError

from .value_objects import PasswordHash


class PasswordHasher(Protocol):
    def hash(
        self,
        password: str,
    ) -> PasswordHash: ...

    def verify(
        self,
        password: str,
        password_hash: PasswordHash,
    ) -> bool: ...

    def needs_rehash(
        self,
        password_hash: PasswordHash,
    ) -> bool: ...


class Argon2PasswordHasher(PasswordHasher):
    def __init__(
        self,
    ) -> None:
        self._hasher = Argon2Hasher()

    def hash(
        self,
        password: str,
    ) -> PasswordHash:
        return PasswordHash(
            self._hasher.hash(password),
        )

    def verify(
        self,
        password: str,
        password_hash: PasswordHash,
    ) -> bool:
        try:
            return self._hasher.verify(
                password_hash.value,
                password,
            )
        except (VerifyMismatchError, VerificationError):
            return False

    def needs_rehash(
        self,
        password_hash: PasswordHash,
    ) -> bool:
        return self._hasher.check_needs_rehash(
            password_hash.value,
        )
