from typing import Final

from identity.authorization.domain.value_objects import Permission


class UserPermissions:
    READ: Final = Permission("users:read")
    CREATE: Final = Permission("users:create")
    UPDATE: Final = Permission("users:update")
    DELETE: Final = Permission("users:delete")
    MANAGE: Final = Permission("users:*")
