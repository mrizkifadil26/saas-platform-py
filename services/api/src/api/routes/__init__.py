from fastapi import APIRouter

from .routes.dashboard.v1 import router as dashboard_v1
from .routes.product.v1 import router as product_v1
# from .routes.health import router as health

router = APIRouter()
# router.include_router(health)

router.include_router(dashboard_v1, prefix="/dashboard/v1", tags=["dashboard"])
router.include_router(product_v1, prefix="/product/v1", tags=["product"])
