from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps_db import get_app_users_session
from db.repo.app_users.api_key_repo import APIKeyRepo

from api.security.session_auth import SessionContext, require_session

router = APIRouter()


@router.get("/me")
async def me(ctx: SessionContext = Depends(require_session)):
    return {
        "user_id": str(ctx.user_id),
        "workspace_id": str(ctx.workspace_id),
        "role": ctx.role,
    }


@router.get("/api-keys")
async def list_api_keys(
    ctx: SessionContext = Depends(require_session),
    db: AsyncSession = Depends(get_app_users_session),
):
    repo = APIKeyRepo(db)
    keys = await repo.list_api_keys(ctx.workspace_id)

    return [{"id": str(k.id), "name": k.name} for k in keys]
