from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from iam.registration.domain.exceptions import (
    EmailVerificationExpiredError,
    IdentityError,
    InvalidCredentialsError,
    InvalidEmailVerificationTokenError,
    UserAlreadyExistsError,
    UserEmailAlreadyVerifiedError,
    UserNotFoundError,
)

_ERROR_RESPONSES: dict[type[IdentityError], tuple[int, str]] = {
    UserAlreadyExistsError: (
        409,
        "User already exists.",
    ),
    UserNotFoundError: (
        404,
        "User not found.",
    ),
    InvalidCredentialsError: (
        400,
        "Invalid credentials.",
    ),
    InvalidEmailVerificationTokenError: (
        400,
        "Invalid email verification token.",
    ),
    EmailVerificationExpiredError: (
        400,
        "Email verification token has expired.",
    ),
    UserEmailAlreadyVerifiedError: (
        409,
        "Email address is already verified.",
    ),
}


async def handle_identity_error(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, IdentityError):
        raise TypeError(
            f"Expected IdentityError, got {type(exc).__name__}",
        )

    status_code, detail = _ERROR_RESPONSES[type(exc)]

    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        IdentityError,
        handle_identity_error,
    )
