from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from iam.shared.domain.exceptions import (
    ConflictError,
    DomainError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ValidationError)
    async def validation_error_handler(
        request: Request,
        exc: ValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": "validation_error", "message": str(exc)},
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_error_handler(
        request: Request,
        exc: UnauthorizedError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"error": "unauthorized", "message": str(exc)},
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_error_handler(
        request: Request,
        exc: ForbiddenError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"error": "forbidden", "message": str(exc)},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(
        request: Request,
        exc: NotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": "not_found", "message": str(exc)},
        )

    @app.exception_handler(ConflictError)
    async def conflict_error_handler(
        request: Request,
        exc: ConflictError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"error": "conflict", "message": str(exc)},
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(
        request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": "domain_error", "message": str(exc)},
        )
