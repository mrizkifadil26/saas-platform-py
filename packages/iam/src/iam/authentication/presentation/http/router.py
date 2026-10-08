from typing import Annotated

from fastapi import APIRouter, Depends, Request

from iam.authentication.application.commands import AuthenticateUserCommand
from iam.authentication.application.use_cases import AuthenticateWithPasswordUseCase
from iam.authentication.presentation.http.schema import LoginRequest, LoginResponse
from iam.dependencies import Dependencies, get_dependencies

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    requestBody: LoginRequest,
    authenticate: Annotated[
        AuthenticateWithPasswordUseCase,
        Depends(get_authenticate_user),
    ],
) -> LoginResponse:
    command = AuthenticateUserCommand(
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        email=requestBody.email,
        password=requestBody.password,
    )

    result = await authenticate.execute(command)

    return LoginResponse.from_result(result)


def get_authenticate_user(
    dependencies: Annotated[
        Dependencies,
        Depends(get_dependencies),
    ],
) -> AuthenticateWithPasswordUseCase:
    return AuthenticateWithPasswordUseCase(
        credential_repository=dependencies.credentials,
        credential_verifier=dependencies.credential_verifier,
        login_throttle=dependencies.login_throttle,
        session_issuer=dependencies.session_issuer,
        clock=dependencies.clock,
    )
