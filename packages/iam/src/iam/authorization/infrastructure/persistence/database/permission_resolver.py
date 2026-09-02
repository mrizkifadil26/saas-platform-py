from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from iam.authorization.application.ports import PermissionResolver
from iam.authorization.domain.permission_set import PermissionSet
from iam.authorization.domain.value_objects import Permission
from iam.identity.domain.value_objects import UserId

from .models import (
    RolePermissionModel,
    UserRoleModel,
)


class SQLAlchemyPermissionResolver(
    PermissionResolver,
):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def resolve(
        self,
        user_id: UserId,
    ) -> PermissionSet:
        stmt = (
            select(distinct(RolePermissionModel.permission))
            .join(
                UserRoleModel,
                UserRoleModel.role_id == RolePermissionModel.role_id,
            )
            .where(UserRoleModel.user_id == user_id.value)
        )

        result = await self._session.execute(stmt)
        permissions = result.scalars()

        return PermissionSet.from_iterable(
            {Permission(permission) for permission in permissions}
        )
