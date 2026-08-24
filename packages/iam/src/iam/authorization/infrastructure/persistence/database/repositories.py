from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from iam.authorization.domain import (
    Role,
    RoleRepository,
    UserRoleRepository,
)
from iam.authorization.domain.value_objects import RoleId
from iam.authorization.infrastructure.persistence.sqlalchemy.orm_mappers import (
    RoleORMMapper,
)
from iam.identity.domain.value_objects import UserId

from .models import RoleModel, RolePermissionModel, UserRoleModel


class SQLAlchemyRoleRepository(
    RoleRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, role: Role) -> None:
        existing = await self._session.get(RoleModel, role.id)
        if existing is None:
            model = self._to_model(role)
            self._session.add(model)
            return

        #

    async def find_by_id(
        self,
        role_id: RoleId,
    ) -> Role | None:
        role_stmt = select(RoleModel).where(
            RoleModel.id == role_id.value,
        )

        role_result = await self._session.execute(role_stmt)
        role_model = role_result.scalar_one_or_none()

        if role_model is None:
            return None

        permission_stmt = select(RolePermissionModel).where(
            RolePermissionModel.role_id == role_model.id
        )
        permission_result = await self._session.execute(permission_stmt)
        permission_models = permission_result.scalars().all()

        return RoleORMMapper.to_domain(
            role_model,
            list(permission_models),
        )

    async def find_by_name(self, name: str) -> Role | None:
        role_stmt = select(RoleModel).where(
            RoleModel.name == name,
        )

        role_result = await self._session.execute(role_stmt)
        role_model = role_result.scalar_one_or_none()

        if role_model is None:
            return None

        permission_stmt = select(RolePermissionModel).where(
            RolePermissionModel.role_id == role_model.id
        )
        permission_result = await self._session.execute(permission_stmt)
        permission_models = permission_result.scalars().all()

        return RoleORMMapper.to_domain(
            role_model,
            list(permission_models),
        )

    @property
    def model_type(self) -> type[RoleModel]:
        return RoleModel

    def _to_domain(self, model: RoleModel) -> Role:
        return RoleORMMapper.to_domain(model)

    def _to_model(self, entity: Role) -> RoleModel:
        return RoleORMMapper.to_model(entity)


class SQLAlchemyUserRoleRepository(
    UserRoleRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def assign_role(
        self,
        user_id: UserId,
        role: Role,
    ) -> None:
        model = UserRoleModel(
            user_id=user_id.value,
            role_id=role.id.value,
        )

        self._session.add(model)

    async def revoke_role(
        self,
        user_id: UserId,
        role: Role,
    ) -> None:
        stmt = delete(UserRoleModel).where(
            UserRoleModel.user_id == user_id.value,
            UserRoleModel.role_id == role.id.value,
        )

        await self._session.execute(stmt)

    async def list_role_ids_for_user(
        self,
        user_id: UserId,
    ) -> list[RoleId]:
        stmt = select(UserRoleModel.role_id).where(
            UserRoleModel.user_id == user_id.value
        )

        result = await self._session.execute(stmt)
        role_ids = result.scalars().all()

        return [RoleId(role_id) for role_id in role_ids]

    @property
    def model_type(self) -> type[UserRoleModel]:
        return UserRoleModel
