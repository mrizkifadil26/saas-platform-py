import hashlib

from iam.sessions.domain import RefreshTokenHasher
from iam.sessions.domain.value_objects import RefreshTokenHash


class SHA256RefreshTokenHasher(RefreshTokenHasher):
    def hash(self, raw_token: str) -> RefreshTokenHash:
        token_hash = hashlib.sha256(
            raw_token.encode(),
        ).hexdigest()

        return RefreshTokenHash(
            token_hash,
        )
