# iam/presentation/http/admin/router.py

from fastapi import APIRouter

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[
        # Depends(require_authenticated_user),
        # Depends(require_admin),
    ],
)


