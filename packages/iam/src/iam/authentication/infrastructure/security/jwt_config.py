from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True, slots=True)
class JWTConfig:
    access_secret_key: str
    refresh_secret_key: str
    registration_secret_key: str

    # algorithm: str
    issuer: str

    access_expiration: timedelta
    refresh_expiration: timedelta
    registration_expiration: timedelta
