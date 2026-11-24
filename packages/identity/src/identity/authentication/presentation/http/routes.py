from dataclasses import dataclass
from typing import cast

from fastapi import APIRouter, Depends, Request, Response, status

from identity.authentication.application.commands import (
    AuthenticateWithPassword,
)
from identity.authentication.application.dto import AuthenticationResult
from identity.sessions.application.commands import RefreshSession
from identity.sessions.application.dto import RefreshSessionResult

from .dependencies import ClockDep, CommandBusDep, RequestContextDep, require_auth
from .schema import (
    LoginRequest,
    LoginResponse,
    RefreshSessionRequest,
    RefreshSessionResponse,
)


@dataclass(frozen=True, slots=True)
class AuthenticationRoutes:
    public: APIRouter
    private: APIRouter


def create_routes() -> AuthenticationRoutes:
    public_router = APIRouter(
        prefix="/auth",
        tags=[
            "authentication",
        ],
    )

    private_router = APIRouter(
        prefix="/auth",
        tags=[
            "authentication",
        ],
        dependencies=[Depends(require_auth)],
    )

    @public_router.post(
        "/login",
        response_model=LoginResponse,
    )
    async def login(
        body: LoginRequest,
        request: Request,
        response: Response,
        bus: CommandBusDep,
        clock: ClockDep,
        context: RequestContextDep,
    ) -> LoginResponse:
        result = cast(
            AuthenticationResult,
            await bus.dispatch(
                AuthenticateWithPassword(
                    email=str(body.email),
                    password=str(body.password),
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                ),
                context=context,
            ),
        )

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

    @public_router.post("/refresh")
    async def refresh_token(
        body: RefreshSessionRequest,
        response: Response,
        bus: CommandBusDep,
        context: RequestContextDep,
    ):
        result = cast(
            RefreshSessionResult,
            await bus.dispatch(
                RefreshSession(
                    refresh_token=str(body.refresh_token),
                ),
                context=context,
            ),
        )

        response.set_cookie(
            key="refresh_token",
            value=result.refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/api/auth",
            max_age=result.refresh_token_max_age,
        )

        return RefreshSessionResponse.from_result(result)
    

    @public_router.post("/password/forgot")
    async def forgot_password(): ...

    # Public (but after clicking forgot password)
    @public_router.post("/password/reset")
    async def reset_password(): ...

    # Private
    @private_router.post("/password/change")
    async def change_password(): ...

    @private_router.post(
        "/logout",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def logout(
        request: Request,
        response: Response,
        bus: CommandBusDep,
        context: RequestContextDep,
        refresh_token: str | None = Cookie(default=None),
    ) -> None:
        if refresh_token is not None:
            await bus.dispatch(
                Logout(refresh_token=refresh_token),
                context=context,
            )

        response.delete_cookie(
            key="refresh_token",
            path="/api/auth",
        )

    return AuthenticationRoutes(
        public=public_router,
        private=private_router,
    )
