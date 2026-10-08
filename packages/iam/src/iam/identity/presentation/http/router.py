from fastapi import APIRouter, Depends, Request, status

from iam.authentication.presentation.http.contexts import AuthenticationContext
from iam.authentication.presentation.http.dependencies import require_authentication
from iam.identity.application.commands import RegisterUserCommand
from iam.identity.application.dto import GetUserResult
from iam.identity.application.use_cases import RegisterUserUseCase

# from iam.identity.application.use_cases import GetUserQuery, GetUserUseCase
from .schema import RegistrationCreateRequest, RegistrationResponse

public_router = APIRouter()


@public_router.post(
    "/registrations",
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationResponse,
)
async def register(
    request: RegistrationCreateRequest,
    register_user: RegisterUserUseCase,
) -> RegistrationResponse:
    result = await register_user.execute(
        RegisterUserCommand(
            email=request.email,
            password=request.password,
            name=request.name,
        )
    )

    return RegistrationResponse(
        registration_id=result.id,
        email=result.user.email,
        # expires_at=result.expires_at,
        status="pending_email_verification",
        expires_at=result.verification_expires_at,
    )


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
