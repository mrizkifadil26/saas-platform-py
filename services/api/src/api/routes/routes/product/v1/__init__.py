from fastapi import APIRouter

from .companies import router as company_router
from .people import router as people_router


router = APIRouter()
router.include_router(company_router, prefix="/companies", tags=["companies"])
router.include_router(people_router, prefix="/people", tags=["people"])
