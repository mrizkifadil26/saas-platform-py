from datetime import datetime, timezone
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.app_users.entitlement import WorkspaceEntitlement


class EntitlementRepo:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_entitlements(
        self,
        workspace_id: uuid.UUID,
    ) -> WorkspaceEntitlement | None:
        stmt = select(WorkspaceEntitlement).where(WorkspaceEntitlement.workspace_id == workspace_id)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def ensure_default_entitlements(
        self, workspace_id: uuid.UUID
    ) -> WorkspaceEntitlement | None:
        entitlement = await self.get_entitlements(workspace_id)
        if entitlement:
            return entitlement

        new_entitlement = WorkspaceEntitlement(
            workspace_id=workspace_id,
            plan="free",
            status="active",
            monthly_lookup_limit=None,
            monthly_enrich_limit=None,
            features={},
            effective_from=datetime.now(timezone.utc),
        )

        self.db.add(new_entitlement)
        await self.db.flush()
        return new_entitlement
