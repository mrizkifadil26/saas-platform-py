from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True, slots=True)
class JWTConfig:
    secret_key: str
    issuer: str
    audience: str
    algorithm: str
    access_token_expiration: timedelta
