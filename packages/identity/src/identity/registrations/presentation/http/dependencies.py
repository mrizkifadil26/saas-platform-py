from typing import Annotated, cast

from fastapi import Depends, Request

from identity.registrations.presentation.http.settings import HTTPSettings
from identity.shared.application.command_bus import CommandBus

# class OIDCRegistrationFlow(Protocol):
#     async def start(self, request: Request) -> RedirectResponse:
#         """Create the authorization redirect and persist OAuth state."""

#     async def verify_callback(
#         self,
#         request: Request,
#     ) -> VerifiedOIDCIdentity:
#         """Validate and consume the OAuth/OIDC callback."""


# def get_oidc_registration_flow(request: Request) -> OIDCRegistrationFlow:
#     return cast(
#         OIDCRegistrationFlow,
#         request.app.state.oidc_registration_flow,
#     )


def get_command_bus(request: Request) -> CommandBus:
    return cast(CommandBus, request.app.state.command_bus)


def get_http_settings(
    request: Request,
) -> HTTPSettings:
    return cast(
        HTTPSettings,
        request.app.state.http_settings,
    )


CommandBusDep = Annotated[
    CommandBus,
    Depends(get_command_bus),
]

HTTPSettingsDep = Annotated[
    HTTPSettings,
    Depends(get_http_settings),
]
