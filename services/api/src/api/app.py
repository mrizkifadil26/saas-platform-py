from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .settings import Settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        title=settings.api_name,
        version=settings.api_version,
    )

    app.state.settings = settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
    )

    return app
