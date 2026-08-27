from iam.authorization.domain import Role, RoleAssignment
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
        permission_set: set[Permission] = {
            Permission(item.permission) for item in permissions
        }

        return Role(
            id=RoleId(model.id),
            _name=model.name,
            _permissions=permission_set,
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
    def to_permission_models(
        role: Role,
    ) -> list[RolePermissionModel]:
        return [
            RolePermissionModel(
                role_id=role.id.value,
                permission=permission.value,
            )
            for permission in role.permissions
        ]


class RoleAssignmentORMMapper:
    @staticmethod
    def to_domain(
        model: UserRoleModel,
    ) -> RoleAssignment:
        return RoleAssignment(
            user_id=UserId(model.user_id),
            role_id=RoleId(model.role_id),
        )

    @staticmethod
    def to_model(
        entity: RoleAssignment,
    ) -> UserRoleModel:
        return UserRoleModel(
            user_id=entity.user_id.value,
            role_id=entity.role_id.value,
        )
