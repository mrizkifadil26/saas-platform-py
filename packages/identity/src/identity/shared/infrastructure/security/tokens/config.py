from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True, slots=True)
class TokenConfig:
    issuer: str
    audience: str
    signing_key: str
    verification_key: str

    access_ttl: timedelta
    refresh_ttl: timedelta