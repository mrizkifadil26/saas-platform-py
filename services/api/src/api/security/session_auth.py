from datetime import datetime, timezone
import uuid
from dataclasses import dataclass

from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps_db import get_app_users_session
from db.repo.app_users.session_repo import SessionRepo
from db.repo.app_users.membership_repo import MembershipRepo
from db.utils.sessions import hash_session_token


@dataclass(frozen=True)
class SessionContext:
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    session_id: uuid.UUID


SESSION_COOKIE_NAME = "px_session"


async def require_session(
    px_session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    app_users_db: AsyncSession = Depends(get_app_users_session),
) -> SessionContext:
    if not px_session:
        raise HTTPException(status_code=401, detail="not_authenticated")

    token_hash = hash_session_token(px_session)

    session_repo = SessionRepo(app_users_db)
    sess = await session_repo.get_active_session_by_token_hash(token_hash)
    if not sess:
        raise HTTPException(status_code=401, detail="invalid_or_expired_session")

    membership_repo = MembershipRepo(app_users_db)
    membership = await membership_repo.get_membership(
        workspace_id=sess.workspace_id,
        user_id=sess.user_id,
    )
    if not membership:
        raise HTTPException(status_code=403, detail="no_membership")

    now = datetime.now(timezone.utc)
    await session_repo.touch_last_session(sess.id, now)

    return SessionContext(
        workspace_id=sess.workspace_id,
        user_id=sess.user_id,
        role=membership.role,
        session_id=sess.id,
    )
