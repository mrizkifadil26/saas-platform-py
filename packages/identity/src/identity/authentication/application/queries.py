from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GetAuthenticationQuery:
    access_token: str
