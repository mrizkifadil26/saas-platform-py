from dataclasses import dataclass
from typing import Annotated, cast

from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from identity.authentication.application.queries import GetAuthenticationQuery
from identity.authentication.application.use_cases import (
    AuthenticateWithPasswordUseCase,
    ForgotPasswordCredentialUseCase,
    ResetPasswordCredentialUseCase,
)
from identity.shared.application.command_bus.bus import CommandBus
from identity.shared.application.request_context import RequestContext
from identity.shared.infrastructure.time.clock import Clock

from .contexts import AuthenticationContext

bearer = HTTPBearer(
    auto_error=False,
)


async def require_auth(
    request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)
) -> AuthenticationContext:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    result = await request.app.state.application.authenticate.execute(
        GetAuthenticationQuery(
            access_token=credentials.credentials,
        )
    )

    return AuthenticationContext(
        user_id=result.user_id,
        session_id=result.session_id,
    )


@dataclass(frozen=True, slots=True)
class AuthenticationUseCase:
    authenticate_with_password: AuthenticateWithPasswordUseCase
    forgot_password: ForgotPasswordCredentialUseCase
    reset_password: ResetPasswordCredentialUseCase


async def get_auth_usecase():
    return AuthenticationUseCase(
        authenticate_with_password=AuthenticateWithPasswordUseCase(),
        forgot_password=ForgotPasswordCredentialUseCase(),
        reset_password=ResetPasswordCredentialUseCase(),
    )


def get_clock(request: Request) -> Clock:
    return cast(
        Clock,
        request.app.state.clock,
    )


ClockDep = Annotated[
    Clock,
    Depends(get_clock),
]


def get_optional_refresh_token(
    refresh_token: Annotated[
        str | None,
        Cookie(),
    ],
) -> str | None:
    return refresh_token


def get_required_refresh_token(
    refresh_token: Annotated[
        str | None,
        Cookie(),
    ],
) -> str:
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    return refresh_token


RefreshTokenOptionalDep = Annotated[
    str | None,
    Depends(get_optional_refresh_token),
]

RefreshTokenRequiredDep = Annotated[
    str | None,
    Depends(get_required_refresh_token),
]


def get_command_bus(request: Request) -> CommandBus:
    return cast(CommandBus, request.app.state.command_bus)


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


CommandBusDep = Annotated[
    CommandBus,
    Depends(get_command_bus),
]


RequestContextDep = Annotated[
    RequestContext,
    Depends(get_request_context),
]
