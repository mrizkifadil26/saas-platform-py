from fastapi import APIRouter

from .container import Container

router = APIRouter()

router.include_router(identity_router)
router.include_router(authn_router)
router.include_router(authz_router)

__all__ = ["Container", "router"]
