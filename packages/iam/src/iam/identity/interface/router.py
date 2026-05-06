from fastapi import APIRouter, Depends, status

from iam.identity.application.commands import RegisterUser
from iam.shared.application.command_bus import CommandBus

from .schemas import RegisterUserRequest

router = APIRouter(prefix="/users", tags=["identity"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def register_user(
    body: RegisterUserRequest,
    command_bus: CommandBus = Depends(),
):
    await command_bus.dispatch(
        RegisterUser(
            email=body.email,
            password=body.password,
        )
    )
