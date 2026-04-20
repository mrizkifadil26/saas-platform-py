import uuid
from datetime import datetime, timezone

from packages.shared.db.src.db.models.app_users.session import Session
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class SessionRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_session_by_token_hash(
        self,
        token_hash: bytes,
    ) -> Session | None:
        now = datetime.now(timezone.utc)
        stmt = (
            select(Session)
            .where(Session.token_hash == token_hash)
            .where(Session.revoked_at.is_(None))
            .where(Session.expires_at > now)
            .limit(1)
        )

        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def touch_last_session(
        self,
        session_id: uuid.UUID,
        when: datetime,
    ) -> bool:
        stmt = (
            update(Session)
            .where(Session.id == session_id)
            .values(last_used_at=when)
            .returning(Session.id)
        )

        res = await self.db.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def revoke_session(
        self,
        session_id: uuid.UUID,
        when: datetime,
    ) -> bool:
        stmt = (
            update(Session)
            .where(Session.id == session_id)
            .values(revoked_at=when)
            .returning(Session.id)
        )

        res = await self.db.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def create_session(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
        token_hash: bytes,
        created_at: datetime,
        expires_at: datetime,
    ) -> Session:
        s = Session(
            user_id=user_id,
            workspace_id=workspace_id,
            token_hash=token_hash,
            created_at=created_at,
            expires_at=expires_at,
            revoked_at=None,
            last_used_at=None,
        )

        self.db.add(s)
        await self.db.flush()

        return s
