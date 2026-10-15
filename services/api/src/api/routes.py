from typing import Annotated

from fastapi import APIRouter, Depends

from .container import AppContainer
from .dependencies import get_container

router = APIRouter()


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(
    container: Annotated[
        AppContainer,
        Depends(get_container),
    ],
) -> dict[str, str]:
    await container.app_db.health()
    await container.redis.health()
    await container.rabbitmq.health()

    return {"status": "ok"}
