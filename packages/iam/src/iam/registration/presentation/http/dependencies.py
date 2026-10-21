from dataclasses import dataclass
from typing import Literal, Protocol, cast

from fastapi import Request
from fastapi.responses import RedirectResponse

from iam.shared.application.command_bus.bus import CommandBus

SameSite = Literal["lax", "strict", "none"]


@dataclass(frozen=True, slots=True)
class RegistrationHTTPSettings:
    oidc_success_redirect_url: str
    cookie_secure: bool = True
    cookie_samesite: SameSite = "lax"
    cookie_domain: str | None = None
    cookie_path: str = "/registrations/current"
    resume_cookie_name: str = "registration_resume"


class OIDCRegistrationFlow(Protocol):
    async def start(self, request: Request) -> RedirectResponse:
        """Create the authorization redirect and persist OAuth state."""

    async def verify_callback(
        self,
        request: Request,
    ) -> VerifiedOIDCIdentity:
        """Validate and consume the OAuth/OIDC callback."""


def get_command_bus(request: Request) -> CommandBus:
    return cast(CommandBus, request.app.state.command_bus)


def get_registration_http_settings(
    request: Request,
) -> RegistrationHTTPSettings:
    return cast(
        RegistrationHTTPSettings,
        request.app.state.registration_http_settings,
    )


def get_oidc_registration_flow(request: Request) -> OIDCRegistrationFlow:
    return cast(
        OIDCRegistrationFlow,
        request.app.state.oidc_registration_flow,
    )
