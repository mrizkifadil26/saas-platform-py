from dataclasses import dataclass

from .value_objects import Permission


@dataclass(slots=True)
class AuthorizationService:
    def authorize(
        self,
        *,
        permissions: set[Permission],
        required: Permission,
    ) -> None:
        if required not in permissions:
            # TODO: raise permission denied error
            raise
