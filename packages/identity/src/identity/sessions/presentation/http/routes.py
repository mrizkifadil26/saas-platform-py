
from fastapi import APIRouter


def create_routes() -> APIRouter:
    router = APIRouter(prefix="/sessions", tags=["sessions"])

    return router

    # @router.post(
    #     "/refresh",
    #     response_model=RefreshResponse,
    # )
    # async def refresh(
    #     response: Response,
    #     refresh_token: Annotated[
    #         str | None,
    #         Depends(get_refresh_token),
    #     ],
    #     refresh_session: Annotated[
    #         RefreshSessionUseCase,
    #         Depends(get_refresh_usecase),
    #     ],
    # ) -> RefreshResponse:
    #     command = RefreshSessionCommand(
    #         refresh_token=refresh_token,
    #     )

    #     result = await refresh_session.execute(command)

    #     response.set_cookie(
    #         key="refresh_token",
    #         value=result.refresh_token,
    #         httponly=True,
    #         secure=True,
    #         samesite="lax",
    #         path="/api/auth",
    #         max_age=result.refresh_token_max_age,
    #     )

    #     return RefreshResponse.from_result(result)
