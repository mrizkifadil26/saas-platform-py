from iam.authorization.domain import Role, UserRole
from iam.authorization.domain.value_objects import Permission, RoleId
from iam.identity.domain.value_objects import UserId

from .models import (
    RoleModel,
    RolePermissionModel,
    UserRoleModel,
)


class RoleORMMapper:
    @staticmethod
    def to_domain(
        model: RoleModel,
        permissions: list[RolePermissionModel],
    ) -> Role:
        permission_sets: set[Permission] = {
            Permission(permission.permission) for permission in permissions
        }

        return Role(
            id=RoleId(model.id),
            name=model.name,
            permissions=permission_sets,
        )

    @staticmethod
    def to_model(
        role: Role,
    ) -> RoleModel:
        return RoleModel(
            id=role.id.value,
            name=role.name,
        )

    @staticmethod
    def update_model(
        model: RoleModel,
        role: Role,
    ) -> None:
        model.name = role.name


class UserRoleORMMapper:
    @staticmethod
    def to_domain(
        model: UserRoleModel,
    ) -> UserRole:
        return UserRole(
            user_id=UserId(model.user_id),
            role_id=RoleId(model.role_id),
        )

    @staticmethod
    def to_model(
        entity: UserRole,
    ) -> UserRoleModel:
        return UserRoleModel(
            user_id=entity.user_id.value,
            role_id=entity.role_id.value,
        )
