from dataclasses import dataclass
from typing import Literal

SameSite = Literal["lax", "strict", "none"]


@dataclass(frozen=True, slots=True)
class CookieSettings:
    name: str
    secure: bool = True
    httponly: bool = True
    samesite: SameSite = "lax"
    domain: str | None = None
    path: str = "/registrations"


@dataclass(frozen=True, slots=True)
class RegistrationCookies:
    resume: CookieSettings


@dataclass(frozen=True, slots=True)
class RegistrationHTTPSettings:
    oidc_success_redirect_url: str

    cookies: RegistrationCookies


@dataclass(frozen=True, slots=True)
class HTTPSettings:
    registration: RegistrationHTTPSettings
