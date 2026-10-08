from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from iam.authentication.application.queries import GetAuthenticationQuery

from .contexts import AuthenticationContext

bearer = HTTPBearer(
    auto_error=False,
)


async def require_authentication(
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
