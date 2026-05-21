import hashlib

from iam.sessions.application import RefreshTokenHasher
from iam.sessions.domain.value_objects import RefreshTokenHash, RefreshTokenSecret


class SHA256RefreshTokenHasher(
    RefreshTokenHasher,
):
    def hash(
        self,
        raw_token: RefreshTokenSecret,
    ) -> RefreshTokenHash:
        token_value = raw_token.unwrap()

        return RefreshTokenHash(
            self._compute_hash(token_value),
        )

    def _compute_hash(
        self,
        raw_token: str,
    ) -> str:
        return hashlib.sha256(
            raw_token.encode(),
        ).hexdigest()
