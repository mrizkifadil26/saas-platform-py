from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from iam.authentication.application.queries import GetAuthenticationQuery
from iam.authentication.application.use_cases import (
    AuthenticateWithPasswordUseCase,
    ForgotPasswordCredentialUseCase,
    ResetPasswordCredentialUseCase,
)

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
