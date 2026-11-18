from collections.abc import Callable
from typing import Annotated, Awaitable

from fastapi import Depends, HTTPException, status
from identity.authorization.application.services import AuthorizationService
from identity.authorization.domain.value_objects import Permission
from identity.identity.domain.value_objects import UserId


def require_permission(
    permission: Permission,
) -> Callable[..., Awaitable[None]]:
    async def dependency(
        user_id: Annotated[UserId, Depends(get_current_user_id)],
        authorization: Annotated[AuthorizationService, Depends(get_authorization_service)],
    ) -> None:
        allowed = await authorization.authorize(
            user_id=user_id,
            required=permission,
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

    return dependency
