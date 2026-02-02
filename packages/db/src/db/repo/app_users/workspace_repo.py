import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.app_users.membership import Membership
from db.models.app_users.workspace import Workspace


class WorkspaceRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_workspace_by_id(self, workspace_id: uuid.UUID) -> Workspace | None:
        res = await self.db.execute(select(Workspace).filter(Workspace.id == workspace_id))

        return res.scalar_one_or_none()

    async def get_workspace_by_slug(self, slug: str) -> Workspace | None | None:
        res = await self.db.execute(select(Workspace).filter(Workspace.slug == slug))

        return res.scalar_one_or_none()

    async def create_workspace(self, name: str, slug: str) -> Workspace:
        new_workspace = Workspace(name=name, slug=slug)

        self.db.add(new_workspace)
        await self.db.flush()
        # self.db.commit()
        return new_workspace

    async def get_workspaces_by_user_id(self, user_id: uuid.UUID) -> list[Workspace]:
        stmt = (
            select(Workspace)
            .join(Membership, Membership.workspace_id == Workspace.id)
            .where(Membership.user_id == user_id)
        )

        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def deactivate_workspace(self, workspace_id: uuid.UUID) -> bool:
        res = await self.db.execute(
            update(Workspace)
            .where(Workspace.id == workspace_id)
            .values(is_active=False)
            .returning(Workspace.id)
        )

        return res.scalar_one_or_none() is not None
