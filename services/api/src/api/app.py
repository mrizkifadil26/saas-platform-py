from fastapi import FastAPI

from .lifespan import lifespan
from .settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=settings.cors_allow_origins,
    #     allow_credentials=settings.cors_allow_credentials,
    #     allow_methods=settings.cors_allow_methods,
    #     allow_headers=settings.cors_allow_headers,
    # )

    register_middleware(app)
    register_exception_handlers(app)
    register_routes(app)

    return app


def register_middleware(app: FastAPI) -> None:
    # app.add_middleware(RequestIdMiddleware)
    ...


def register_exception_handlers(app: FastAPI) -> None: ...


def register_routes(app: FastAPI) -> None: ...


app = create_app()
