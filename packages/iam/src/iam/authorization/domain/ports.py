from typing import Protocol

from iam.authorization.domain.value_objects import Permission
from iam.identity.domain.value_objects import UserId


class PermissionResolver(Protocol):
    async def resolve_permissions_for_user(
        self,
        user_id: UserId,
    ) -> set[Permission]: ...
