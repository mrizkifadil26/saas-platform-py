from fastapi import FastAPI

from iam.registration.domain.exceptions import IdentityError

from .errors import handle_identity_error
from .router import router as identity_router


def register(app: FastAPI) -> None:
    app.include_router(
        identity_router,
        prefix="/iam",
    )

    app.add_exception_handler(
        IdentityError,
        handle_identity_error,
    )
