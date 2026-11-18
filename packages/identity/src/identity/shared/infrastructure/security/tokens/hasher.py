import hashlib
import hmac


class TokenHasher:
    def __init__(self, *, secret: bytes) -> None:
        if len(secret) < 32:
            raise ValueError("Token hashing secret must be at least 32 bytes")

        self._secret = secret

    def hash(self, token: str) -> str:
        digest = hmac.new(
            self._secret,
            token.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return digest

    def verify(
        self,
        token: str,
        expected_digest: str,
    ) -> bool:
        actual_digest = self.hash(token)

        return hmac.compare_digest(
            actual_digest,
            expected_digest,
        )
