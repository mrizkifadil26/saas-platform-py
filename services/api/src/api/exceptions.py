import logging

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "Unhandled application exception",
        exc_info=exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "code": "internal_server_error",
            "message": "An unexpected error occurred.",
        },
    )
