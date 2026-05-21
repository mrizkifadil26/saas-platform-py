from typing import Protocol

from iam.sessions.domain.value_objects import RefreshTokenHash, RefreshTokenSecret


class RefreshTokenHasher(Protocol):
    def hash(
        self,
        raw_token: RefreshTokenSecret,
    ) -> RefreshTokenHash: ...


class RefreshTokenGenerator(Protocol):
    def generate(
        self,
    ) -> RefreshTokenSecret: ...
