import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedAPIKey:
    token: str
    last4: str


def generate_api_key(*, nbytes: int = 32) -> GeneratedAPIKey:
    """Generates a new API key token and its last 4 characters."""
    raw = secrets.token_bytes(nbytes)
    token = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    last4 = token[-4:]
    return GeneratedAPIKey(token=token, last4=last4)


def hash_token(*, token: str, pepper: str) -> str:
    """Hashes the given API key token using SHA-256."""
    if not pepper:
        raise ValueError("Pepper must not be empty")

    mac = hmac.new(
        pepper.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"hmac_sha256${mac}"
