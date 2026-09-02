from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from iam.authorization.domain import (
    Role,
    RoleAssignmentRepository,
    RoleRepository,
)
from iam.authorization.domain.value_objects import RoleId
from iam.identity.domain.value_objects import UserId

from .models import RoleModel, RolePermissionModel, UserRoleModel
from .orm_mappers import (
    RoleORMMapper,
)


class SQLAlchemyRoleRepository(
    RoleRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, role: Role) -> None:
        role_model = self._to_model(role)
        permission_models = RoleORMMapper.to_permission_models(role)

        self._session.add(role_model)
        self._session.add_all(permission_models)

    async def save(self, role: Role) -> None:
        existing = await self._session.get(RoleModel, role.id)
        if existing is None:
            model = self._to_model(role)
            self._session.add(model)
            return

        # TODO: the rest of the operation is here
        return

    async def find_by_id(
        self,
        role_id: RoleId,
    ) -> Role | None:
        stmt = (
            select(RoleModel)
            .options(selectinload(RoleModel.permissions))
            .where(
                RoleModel.id == role_id.value,
            )
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None

        return self._to_domain(
            model,
            list(model.permissions),
        )

    async def find_by_name(
        self,
        name: str,
    ) -> Role | None:
        stmt = (
            select(RoleModel)
            .options(selectinload(RoleModel.permissions))
            .where(
                RoleModel.name == name,
            )
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None

        return RoleORMMapper.to_domain(
            model,
            list(model.permissions),
        )

    async def delete(
        self,
        role_id: RoleId,
    ) -> None:
        stmt = delete(RoleModel).where(
            RoleModel.id == role_id.value,
        )

        await self._session.execute(stmt)

    @staticmethod
    def _to_domain(
        model: RoleModel,
        permissions: list[RolePermissionModel],
    ) -> Role:
        return RoleORMMapper.to_domain(
            model,
            permissions,
        )

    @staticmethod
    def _to_model(
        entity: Role,
    ) -> RoleModel:
        return RoleORMMapper.to_model(entity)

    @property
    def model_type(self) -> type[RoleModel]:
        return RoleModel


class SQLAlchemyRoleAssignmentRepository(
    RoleAssignmentRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def assign_role(
        self,
        user_id: UserId,
        role_id: RoleId,
    ) -> None:
        model = UserRoleModel(
            user_id=user_id.value,
            role_id=role_id.value,
        )

        self._session.add(model)

    async def revoke_role(
        self,
        user_id: UserId,
        role_id: RoleId,
    ) -> None:
        stmt = delete(UserRoleModel).where(
            UserRoleModel.user_id == user_id.value,
            UserRoleModel.role_id == role_id.value,
        )

        await self._session.execute(stmt)

    async def is_assigned(
        self,
        user_id: UserId,
        role_id: RoleId,
    ) -> bool:
        stmt = (
            select(UserRoleModel.user_id)
            .where(
                UserRoleModel.user_id == user_id.value,
                UserRoleModel.role_id == role_id.value,
            )
            .limit(1)
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        return model is not None

    async def list_role_ids_for_user(
        self,
        user_id: UserId,
    ) -> list[RoleId]:
        stmt = select(UserRoleModel.role_id).where(
            UserRoleModel.user_id == user_id.value,
        )

        result = await self._session.execute(stmt)
        role_ids = result.scalars().all()

        return [RoleId(role_id) for role_id in role_ids]

    @property
    def model_type(self) -> type[UserRoleModel]:
        return UserRoleModel
