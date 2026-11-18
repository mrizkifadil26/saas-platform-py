from typing import cast

from fastapi import APIRouter, Response

from identity.registrations.presentation.http.dependencies import CommandBusDep, RequestContextDep
from identity.sessions.application.commands import RefreshSession
from identity.sessions.application.dto import RefreshSessionResult
from identity.sessions.presentation.http.schemas import RefreshSessionRequest

router = APIRouter()


def create_routes():
    router = APIRouter(
        prefix="/sessions",
        tags=[
            "sessions"
        ]
    )
    
    @router.post("/refresh")
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
            )
        )

        response.set_cookie()

        return RefreshResponse.from_result(result)
