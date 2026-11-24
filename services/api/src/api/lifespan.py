from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .container import AppContainer
from .settings import Settings


def create_lifespan(settings: Settings):
    @asynccontextmanager
    async def lifespan(
        app: FastAPI,
    ) -> AsyncGenerator[None, None]:
        container = await AppContainer.create(settings)
        app.state.container = container

        try:
            await container.start()
            yield
        finally:
            await container.stop()

    return lifespan
