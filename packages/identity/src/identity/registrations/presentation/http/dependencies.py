from typing import Annotated, cast

from fastapi import Depends, Request

from identity.registrations.presentation.http.settings import HTTPSettings
from identity.shared.application.command_bus import CommandBus
from identity.shared.application.request_context import RequestContext
from identity.shared.infrastructure.time.clock import Clock

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


def get_request_context(
    request: Request,
) -> RequestContext:
    return RequestContext(
        request_id=request.state.request_id,
        client_ip=get_client_ip(request),
        user_agent=get_user_agent(request),
    )


def get_client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def get_user_agent(request: Request) -> str | None:
    return request.headers.get("user-agent")


def get_clock(request: Request) -> Clock:
    return cast(
        Clock,
        request.app.state.clock,
    )


CommandBusDep = Annotated[
    CommandBus,
    Depends(get_command_bus),
]

ClockDep = Annotated[
    Clock,
    Depends(get_clock),
]

HTTPSettingsDep = Annotated[
    HTTPSettings,
    Depends(get_http_settings),
]

RequestContextDep = Annotated[
    RequestContext,
    Depends(get_request_context),
]
