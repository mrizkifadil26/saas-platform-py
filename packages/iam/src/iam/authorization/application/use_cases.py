from dataclasses import dataclass

from iam.authorization.domain import (
    AuthorizationService,
    PermissionCacheInvalidator,
    PermissionResolver,
    Role,
    RoleRepository,
    UserRoleRepository,
)
from iam.authorization.domain.value_objects import Permission

from .commands import (
    AssignRoleToUserCommand,
    AuthorizeCommand,
    CreateRoleCommand,
    GrantPermissionToRoleCommand,
)
from .dto import AuthorizationResult, RoleDTO


@dataclass(slots=True)
class CreateRoleUseCase:
    role_repository: RoleRepository

    async def execute(
        self,
        command: CreateRoleCommand,
    ) -> RoleDTO:
        existing = await self.role_repository.find_by_name(
            command.name,
        )

        if existing is not None:
            # TODO: raise role already exists error
            raise

        role = Role.create(
            name=command.name,
        )
        await self.role_repository.save(role)
        # TODO: commit uow here

        return RoleDTO(
            id=role.id.unwrap(),
            name=role.name,
        )


@dataclass(slots=True)
class GrantPermissionToRoleUseCase:
    role_repository: RoleRepository
    permission_cache_invalidator: PermissionCacheInvalidator

    async def execute(
        self,
        command: GrantPermissionToRoleCommand,
    ) -> None:
        role = await self.role_repository.find_by_id(
            command.role_id,
        )

        if role is None:
            # TODO: raise role not found error
            raise

        role.grant(Permission(command.permission))

        # TODO: commit uow here

        await self.permission_cache_invalidator.invalidate_role_permissions(
            role.id,
        )


@dataclass(slots=True)
class AssignRoleToUser:
    role_repository: RoleRepository
    user_role_repository: UserRoleRepository
    permission_cache_invalidator: PermissionCacheInvalidator

    async def execute(
        self,
        command: AssignRoleToUserCommand,
    ) -> None:
        role = await self.role_repository.find_by_id(command.role_id)

        if role is None:
            # TODO: raise role not found error
            raise

        await self.user_role_repository.assign_role(
            user_id=command.user_id,
            role=role,
        )

        # TODO: commit uow here

        await self.permission_cache_invalidator.invalidate_user_permissions(
            command.user_id,
        )


@dataclass(slots=True)
class AuthorizeUseCase:
    permission_resolver: PermissionResolver
    authorization_service: AuthorizationService

    async def execute(
        self,
        command: AuthorizeCommand,
    ) -> AuthorizationResult:
        permissions = await self.permission_resolver.resolve_permissions_for_user(
            command.user_id,
        )

        allowed = Permission(command.permission) in permissions

        return AuthorizationResult(allowed)
