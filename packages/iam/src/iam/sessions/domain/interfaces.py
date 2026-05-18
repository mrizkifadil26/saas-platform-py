from typing import Protocol

from iam.sessions.domain.value_objects import RefreshTokenHash


class RefreshTokenHasher(Protocol):
    def hash(
        self,
        raw_token: str,
    ) -> RefreshTokenHash: ...


class RefreshTokenGenerator(Protocol):
    def generate(self) -> str: ...
