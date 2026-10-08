from fastapi import APIRouter

from .container import AppContainer

router = APIRouter()


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(container: AppContainer) -> dict[str, str]:
    await container.infrastructure.app_db.health()
    await container.infrastructure.redis.health()
    await container.infrastructure.rabbitmq.health()

    return {"status": "ok"}
