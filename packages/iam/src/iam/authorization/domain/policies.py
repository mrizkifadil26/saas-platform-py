from dataclasses import dataclass

from iam.authorization.domain.value_objects import Permission


@dataclass(frozen=True, slots=True)
class UserPolicies:
    READ = Permission("users.read")
    CREATE = Permission("users.create")
    UPDATE = Permission("users.update")
    DELETE = Permission("users.delete")
