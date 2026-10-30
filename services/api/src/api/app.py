from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from identity.registrations.presentation.http.errors import REGISTRATION_ERRORS
from identity.shared.infrastructure.http.errors import HTTPErrorRegistry, create_error_handler
from identity.shared.kernel.exceptions import DomainError

from .lifespan import create_lifespan
from .middlewares import RequestIdMiddleware
from .settings import Settings, get_settings


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=create_lifespan(settings),
    )

    app.state.settings = settings

    register_middleware(app, settings)
    register_exception_handlers(app)
    register_routes(app)

    return app


def register_middleware(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(RequestIdMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_exception_handlers(app: FastAPI) -> None:
    # app.add_exception_handler(Exception, unexpected_exception_handler)
    registry = HTTPErrorRegistry(
        REGISTRATION_ERRORS,
    )

    app.add_exception_handler(
        DomainError,
        create_error_handler(registry),
    )


def register_routes(app: FastAPI) -> None: ...


app = create_app()
