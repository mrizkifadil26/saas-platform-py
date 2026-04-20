import uuid
from datetime import datetime, timezone

from packages.shared.db.src.db.models.app_users.audit_log import AuditLog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AuditRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def write(
        self,
        *,
        action: str,
        workspace_id: uuid.UUID | None = None,
        actor_user_id: uuid.UUID | None = None,
        actor_api_key_id: uuid.UUID | None = None,
        target_type: str | None = None,
        target_id: uuid.UUID | None = None,
        ip: str | None = None,
        user_agent: str | None = None,
        meta: dict | None = None,
    ):
        log = AuditLog(
            workspace_id=workspace_id,
            actor_user_id=actor_user_id,
            actor_api_key_id=actor_api_key_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            ip=ip,
            user_agent=user_agent,
            meta=meta or {},
            created_at=datetime.now(timezone.utc),
        )

        self.db.add(log)
        await self.db.flush()
        return log

    async def list_by_workspace(
        self,
        workspace_id: uuid.UUID,
        limit: int | None = None,
    ) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.workspace_id == workspace_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )

        res = await self.db.execute(stmt)
        return list(res.scalars().all())
