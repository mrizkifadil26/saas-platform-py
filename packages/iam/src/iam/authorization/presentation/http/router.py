from fastapi import APIRouter, Depends, Request

from iam.authentication.presentation.http.contexts import AuthenticationContext
from iam.authentication.presentation.http.dependencies import require_authentication
from iam.identity.application.dto import GetUserResult
from iam.identity.application.use_cases import GetUserQuery, GetUserUseCase

public_router = APIRouter()


@public_router.post("/email-verification/verify")
async def verify_email() -> None: ...


@public_router.post("/email-verification/resend")
async def resend_email_verification() -> None: ...


private_router = APIRouter()


@private_router.get("")
async def get_me(
    request: Request,
    authentication: AuthenticationContext = Depends(require_authentication),
) -> GetUserResult:
    use_case: GetUserUseCase = request.app.state.get_user
    query = GetUserQuery(user_id=authentication.user_id)

    return await use_case.execute(query)


admin_router = APIRouter()


@admin_router.get("/users")
async def list_users() -> None: ...


@admin_router.get("/users/{user_id}")
async def get_user(user_id: str) -> None: ...


@admin_router.post("/users")
async def create_user() -> None: ...


@admin_router.post("/users/{user_id}/disable")
async def disable_user(user_id: str) -> None: ...


@admin_router.post("/users/{user_id}/enable")
async def enable_user(user_id: str) -> None: ...


@admin_router.post("/users/{user_id}/reset-password")
async def reset_password(user_id: str) -> None: ...


router = APIRouter()

router.include_router(public_router)
router.include_router(private_router)
router.include_router(admin_router)
