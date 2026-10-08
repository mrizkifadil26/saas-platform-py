from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register")
async def register() -> None: ...


@router.post("/login")
async def login() -> None: ...


@router.post("/password/forgot")
async def forgot_password() -> None: ...


@router.post("/password/reset")
async def reset_password() -> None: ...
