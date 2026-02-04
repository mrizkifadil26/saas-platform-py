from dataclasses import dataclass
import uuid

from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from db.repo.app_users.api_key_repo import APIKeyRepo
from db.utils.api_keys import hash_token
from api.deps_db import get_app_users_session


@dataclass(frozen=True)
class ApiKeyContext:
    workspace_id: uuid.UUID
    api_key_id: uuid.UUID


async def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-Api-Key"),
    authorization: str | None = Header(default=None, alias="Authorizaton"),
    app_users_db: AsyncSession = Depends(get_app_users_session),
) -> ApiKeyContext:
    token = None
    if x_api_key:
        token = x_api_key.strip()
    elif authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()

    if not token:
        raise HTTPException(status_code=401, detail="missing_api_key")

    repo = APIKeyRepo(app_users_db)
    key = await repo.get_by_hash(hash_token(token=token, pepper="mantap"))

    if not key:
        raise HTTPException(status_code=401, detail="invalid_api_key")

    return ApiKeyContext(
        workspace_id=key.workspace_id,
        api_key_id=key.id,
    )
