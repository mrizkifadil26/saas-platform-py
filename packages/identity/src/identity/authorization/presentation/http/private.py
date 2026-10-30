from fastapi import APIRouter

from .public import router as auth_router

router = APIRouter(
    prefix="/me",
    tags=["identity"],
    # depends require authenticated user / context
)


@auth_router.post("/logout")
async def logout() -> None: ...


@router.get("/sessions")
async def list_sessions() -> None: ...


@router.delete("/sessions/{session_id}")
async def revoke_session(session_id: str) -> None: ...


@router.delete("/sessions")
async def revoke_all_sessions() -> None: ...


@router.post("/password/change")
async def change_password() -> None: ...
