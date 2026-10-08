from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .container import AppContainer
from .settings import get_settings


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncGenerator[None, None]:
    container = await AppContainer.create(get_settings())
    container: AppContainer = app.state.container

    try:
        await container.start()
        yield
    finally:
        await container.stop()
