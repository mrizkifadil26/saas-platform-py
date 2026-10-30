from typing import Annotated

from fastapi import APIRouter, Depends, Request
from identity.authentication.application.commands import AuthenticateUserCommand
from identity.authentication.application.use_cases import AuthenticateWithPasswordUseCase
from identity.authentication.presentation.http.dependencies import get_auth_usecase
from identity.authentication.presentation.http.schema import (
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
    requestBody: LoginRequest,
    authentication: Annotated[
        AuthenticateWithPasswordUseCase,
        Depends(get_auth_usecase),
    ],
) -> LoginResponse:
    command = AuthenticateUserCommand(
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        email=requestBody.email,
        password=requestBody.password,
    )

    result = await authentication.execute(command)

    return LoginResponse.from_result(result)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
) -> LogoutResponse: ...


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
