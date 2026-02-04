import uuid
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.app_users.user import User
from db.models.app_users.membership import Membership


class MembershipRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_membership(
        self,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
        role: str = "member",
    ) -> Membership:
        membership = Membership(
            user_id=user_id,
            workspace_id=workspace_id,
            role=role,
        )

        self.db.add(membership)
        await self.db.flush()

        return membership

    async def remove_membership(self, membership: Membership) -> bool:
        res = await self.db.execute(
            delete(Membership)
            .where(
                Membership.workspace_id == membership.workspace_id,
                Membership.user_id == membership.user_id,
            )
            .returning(Membership.id)
        )

        return res.scalar_one_or_none() is not None

    async def list_all_memberships(self, workspace_id: uuid.UUID) -> list[tuple[Membership, User]]:
        stmt = (
            select(Membership, User)
            .join(User, User.id == Membership.user_id)
            .where(Membership.workspace_id == workspace_id)
        )
        res = await self.db.execute(stmt)

        return list(res.tuples().all())

    async def set_role(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str,
    ) -> bool:
        res = await self.db.execute(
            update(Membership)
            .where(
                Membership.workspace_id == workspace_id,
                Membership.user_id == user_id,
            )
            .values(role=role)
            .returning(Membership.id)
        )

        return res.scalar_one_or_none() is not None

    async def count_memberships(self, workspace_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Membership)
            .where(Membership.workspace_id == workspace_id)
        )
        res = await self.db.execute(stmt)

        return int(res.scalar_one())

    async def get_membership(
        self,
        *,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Membership | None:
        stmt = (
            select(Membership)
            .where(Membership.workspace_id == workspace_id)
            .where(Membership.user_id == user_id)
            .limit(1)
        )

        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()
