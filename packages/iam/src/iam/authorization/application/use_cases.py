import json
from dataclasses import dataclass

from iam.authorization.domain import (
    PermissionSet,
    Role,
    RoleAssignmentRepository,
    RoleRepository,
)
from iam.authorization.domain.value_objects import Permission, RoleId
from iam.identity.domain.value_objects.user_id import UserId
from iam.shared.application.cache import Cache

from .commands import (
    AssignRoleToUserCommand,
    CreateRoleCommand,
    GrantPermissionToRoleCommand,
    RevokePermissionFromRoleCommand,
    UnassignRoleFromUserCommand,
)
from .dto import AuthorizationResult, RoleDTO
from .ports import PermissionCacheInvalidator, PermissionResolver
from .queries import (
    CheckPermissionQuery,
    FindRoleByNameQuery,
    GetRoleQuery,
    ListUserRoleIdsQuery,
)


@dataclass(slots=True)
class CreateRoleUseCase:
    role_repository: RoleRepository

    async def execute(
        self,
        command: CreateRoleCommand,
    ) -> RoleDTO:
        role = await self.role_repository.find_by_name(
            command.name,
        )
        if role is not None:
            # TODO: raise role already exists error
            raise

        role = Role.create(
            name=command.name,
            permissions=command.permissions,
        )

        # use save instead of add
        # await self.role_repository.save(role)
        await self.role_repository.add(role)
        # TODO: commit uow here

        return RoleDTO(
            id=role.id.value,
            name=role.name,
            permissions=frozenset(str(permission) for permission in role.permissions),
        )


@dataclass(slots=True)
class RenameRoleUseCase:
    role_repository: RoleRepository

    async def execute(
        self,
        command: CreateRoleCommand,
    ) -> RoleDTO:
        role = await self.role_repository.find_by_name(command.name)
        if role is None:
            # TODO: raise role not found
            raise

        role.rename(name=command.name)
        await self.role_repository.save(role)
        # TODO: commit uow here

        return RoleDTO(
            id=role.id.value,
            name=role.name,
            permissions=frozenset(str(permission) for permission in role.permissions),
        )


@dataclass(slots=True)
class GrantPermissionToRoleUseCase:
    role_repository: RoleRepository
    permission_cache_invalidator: PermissionCacheInvalidator

    async def execute(
        self,
        command: GrantPermissionToRoleCommand,
    ) -> None:
        role = await self.role_repository.find_by_id(command.role_id)
        if role is None:
            # TODO: raise role not found error
            raise

        role.grant_permission(command.permission)
        await self.role_repository.save(role)
        # TODO: commit uow here

        # TODO: need to invalidate cache when commit succeeds
        await self.permission_cache_invalidator.invalidate_role_permissions(
            role.id,
        )


@dataclass(slots=True)
class RevokePermissionFromUserUseCase:
    role_repository: RoleRepository
    permission_cache_invalidator: PermissionCacheInvalidator

    async def execute(
        self,
        command: RevokePermissionFromRoleCommand,
    ) -> None:
        role = await self.role_repository.find_by_id(command.role_id)
        if role is None:
            # TODO: raise role not found error
            raise

        role.revoke_permission(command.permission)
        await self.role_repository.save(role)
        # TODO: commit uow here

        # TODO: need to invalidate cache when commit succeeds
        await self.permission_cache_invalidator.invalidate_role_permissions(
            command.role_id,
        )


@dataclass(slots=True)
class AssignRoleToUserUseCase:
    role_repository: RoleRepository
    role_assignment_repository: RoleAssignmentRepository
    permission_cache_invalidator: PermissionCacheInvalidator

    async def execute(
        self,
        command: AssignRoleToUserCommand,
    ) -> None:
        role = await self.role_repository.find_by_id(command.role_id)
        if role is None:
            # TODO: raise role not found error
            raise

        if await self.role_assignment_repository.is_assigned(
            user_id=command.user_id,
            role_id=command.role_id,
        ):
            return

        await self.role_assignment_repository.assign_role(
            user_id=command.user_id,
            role_id=command.role_id,
        )
        # TODO: commit uow here

        # TODO: need to invalidate cache when commit succeeds
        await self.permission_cache_invalidator.invalidate_user_permissions(
            command.user_id,
        )


@dataclass(slots=True)
class UnassignRoleFromUserUseCase:
    role_repository: RoleRepository
    role_assignment_repository: RoleAssignmentRepository
    permission_cache_invalidator: PermissionCacheInvalidator

    async def execute(
        self,
        command: UnassignRoleFromUserCommand,
    ) -> None:
        role = await self.role_repository.find_by_id(command.role_id)
        if role is None:
            # TODO: raise role not found error
            raise

        if await self.role_assignment_repository.is_assigned(
            user_id=command.user_id,
            role_id=command.role_id,
        ):
            return

        await self.role_assignment_repository.revoke_role(
            user_id=command.user_id,
            role_id=command.role_id,
        )
        # TODO: commit uow here

        # TODO: need to invalidate cache when commit succeeds
        await self.permission_cache_invalidator.invalidate_user_permissions(
            command.user_id,
        )


@dataclass(slots=True)
class GetRoleUseCase:
    role_repository: RoleRepository

    async def execute(
        self,
        query: GetRoleQuery,
    ) -> RoleDTO:
        role = await self.role_repository.find_by_id(query.role_id)
        if role is None:
            # raise role not found
            raise

        return RoleDTO(
            id=role.id.value,
            name=role.name,
            permissions=frozenset(str(permission) for permission in role.permissions),
        )


@dataclass(slots=True)
class FindRoleByNameUseCase:
    role_repository: RoleRepository

    async def execute(
        self,
        query: FindRoleByNameQuery,
    ) -> RoleDTO | None:
        role = await self.role_repository.find_by_name(query.name)
        if role is None:
            # raise role not found
            raise

        return RoleDTO(
            id=role.id.value,
            name=role.name,
            permissions=frozenset(str(permission) for permission in role.permissions),
        )


@dataclass(slots=True)
class ListUserRoleIdsUseCase:
    role_assignment_repository: RoleAssignmentRepository

    async def execute(
        self,
        query: ListUserRoleIdsQuery,
    ) -> list[RoleId]:
        role_ids = await self.role_assignment_repository.list_role_ids_for_user(
            user_id=query.user_id,
        )

        return role_ids


@dataclass(slots=True)
class CheckPermissionUseCase:
    permission_resolver: PermissionResolver
    cache: Cache
    cache_ttl: int = 300

    async def execute(
        self,
        query: CheckPermissionQuery,
    ) -> AuthorizationResult:
        key = self._cache_key(
            query.user_id,
        )

        cached = await self.cache.get(key)
        if cached is not None:
            permissions = self._deserialize(
                cached,
            )
        else:
            resolved = await self.permission_resolver.resolve_permissions_for_user(
                query.user_id,
            )

            permissions = PermissionSet.from_iterable(
                resolved,
            )

            await self.cache.set(
                key,
                self._serialize(permissions),
                ttl=self.cache_ttl,
            )

        is_allowed = permissions.allows(query.permission)

        if not is_allowed:
            # Raise Permission Denied error
            raise

        return AuthorizationResult(
            allowed=is_allowed,
        )

    @staticmethod
    def _cache_key(
        user_id: UserId,
    ) -> str:
        return f"iam:authorization:user:{user_id}:permissions:v1"

    @staticmethod
    def _serialize(
        permissions: PermissionSet,
    ) -> str:
        return json.dumps(
            [str(permission) for permission in permissions],
        )

    @staticmethod
    def _deserialize(
        value: str,
    ) -> PermissionSet:
        raw_permissions = json.loads(value)

        return PermissionSet(
            permissions=frozenset(
                Permission(permission) for permission in raw_permissions
            ),
        )
