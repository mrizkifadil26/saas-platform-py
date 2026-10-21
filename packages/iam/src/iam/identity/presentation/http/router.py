from fastapi import APIRouter, Depends, HTTPException, Request, status

from iam.authentication.presentation.http.dependencies import require_auth
from iam.authorization.domain.permission_catalog import UserPermissions
from iam.authorization.presentation.http.dependencies import require_permission
from iam.identity.presentation.http.dependencies import VerifyEmailUseCaseDep
from iam.registration.application.commands import RegisterUserCommand, VerifyEmailCommand
from iam.registration.application.dto import GetUserResult
from iam.registration.application.handlers import RegisterUserUseCase
from iam.registration.domain.exceptions import (
    EmailVerificationExpiredError,
    InvalidEmailVerificationTokenError,
    UserEmailAlreadyVerifiedError,
    UserNotFoundError,
)

from .schema import (
    EmailVerificationRequest,
    EmailVerificationResponse,
    RegistrationRequest,
    RegistrationResponse,
)

public_router = APIRouter()


@public_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationResponse,
)
async def register(
    request: RegistrationRequest,
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
async def verify_email(
    request: EmailVerificationRequest,
    use_case: VerifyEmailUseCaseDep,
) -> EmailVerificationResponse:
    command = VerifyEmailCommand(request.token)

    try:
        result = await use_case.execute(command)
    except InvalidEmailVerificationTokenError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token",
        ) from exc
    except EmailVerificationExpiredError as exc:
        raise HTTPException(
            status_code=400,
            detail="Email verification token has expired",
        ) from exc
    except UserEmailAlreadyVerifiedError as exc:
        raise HTTPException(
            status_code=409,
            detail="Email address is already verified",
        ) from exc
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        ) from exc

    return EmailVerificationResponse.from_result(result)


@public_router.post("/email-verification/resend")
async def resend_email_verification() -> None: ...


private_router = APIRouter(
    dependencies=[
        Depends(require_auth),
    ],
)


@private_router.get("/me")
async def get_me(request: Request) -> GetUserResult:
    # use_case: GetUserUseCase = request.app.state.get_user
    # query = GetUserQuery(user_id=authentication.user_id)

    return await use_case.execute(query)


admin_router = APIRouter(
    dependencies=[
        Depends(require_auth),
    ],
)


@admin_router.get(
    "/users",
    dependencies=Depends(
        require_permission(UserPermissions.READ),
    ),
)
async def list_users() -> None: ...


@admin_router.get(
    "/users/{user_id}",
    dependencies=Depends(
        require_permission(UserPermissions.READ),
    ),
)
async def get_user(user_id: str) -> None: ...


@admin_router.post(
    "/users",
    dependencies=Depends(
        require_permission(UserPermissions.CREATE),
    ),
)
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
