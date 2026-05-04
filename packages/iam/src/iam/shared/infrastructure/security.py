import secrets
from hashlib import sha256


def generate_secure_token(byte_length: int = 32) -> str:
    return secrets.token_urlsafe(byte_length)


def hash_secret(secret: str) -> str:
    return sha256(secret.encode("utf-8")).hexdigest()


def constant_time_compare(left: str, right: str) -> bool:
    return secrets.compare_digest(left, right)
