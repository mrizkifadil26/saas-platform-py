from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .lifespan import lifespan
from .routes import router as api_router
from .settings import Settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        title=settings.api_name,
        version=settings.api_version,
        lifespan=lifespan,
    )

    app.state.settings = settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    app.include_router(api_router)

    return app
