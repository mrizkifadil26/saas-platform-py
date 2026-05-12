import hashlib
import secrets


class TokenGenerator:
    @staticmethod
    def generate() -> str:
        return secrets.token_urlsafe(64)


class TokenHasher:
    @staticmethod
    def hash(token: str) -> str:
        return hashlib.sha256(
            token.encode(),
        ).hexdigest()
