from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from identity.authentication.application.commands import AuthenticateUserCommand
from identity.authentication.application.use_cases import AuthenticateWithPasswordUseCase

from .dependencies import ClockDep, get_auth_usecase
from .schema import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
)

router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResponse,
)
async def login(
    request: Request,
    response: Response,
    requestBody: LoginRequest,
    authentication: Annotated[
        AuthenticateWithPasswordUseCase,
        Depends(get_auth_usecase),
    ],
    clock: ClockDep,
) -> LoginResponse:
    command = AuthenticateUserCommand(
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        email=requestBody.email,
        password=requestBody.password,
    )

    result = await authentication.execute(command)

    remaining = result.expires_at - clock.now()
    max_age = max(0, int(remaining.total_seconds()))

    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/api/auth",
        max_age=max_age,
    )

    return LoginResponse.from_result(result)

@router.post(
    "/refresh",
    response_model=RefreshResponse,
)
async def refresh(
    response: Response,
    refresh_token: Annotated[
        str | None,
        Depends(get_refresh_token),
    ],
    refresh_session: Annotated[
        RefreshSessionUseCase,
        Depends(get_refresh_usecase),
    ],
) -> RefreshResponse:
    command = RefreshSessionCommand(
        refresh_token=refresh_token,
    )

    result = await refresh_session.execute(command)

    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/api/auth",
        max_age=result.refresh_token_max_age,
    )

    return RefreshResponse.from_result(result)

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    refresh_token: RefreshTokenDep,
    command_bus: CommandBusDep,
) -> LogoutResponse:
    command = LogoutCommand()

    result = await command_bus.execute(command)

    response.delete_cookie(
        key="refresh_token",
        path="/api/auth",
    )

    return LogoutResponse.from_result(result)


# Private
@router.post("/password/setup")
async def setup_password(): ...


@router.post("/password/change")
async def change_password(): ...


# Public
@router.post("/password/forgot")
async def forgot_password(): ...


# Public (but after clicking forgot password)
@router.post("/password/reset")
async def reset_password(): ...
