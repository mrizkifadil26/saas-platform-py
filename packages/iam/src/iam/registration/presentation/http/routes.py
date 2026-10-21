from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, cast

from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import BaseModel

from iam.registration.application.commands import StartEmailPasswordRegistration
from iam.registration.application.dto import RegistrationStarted
from iam.registration.application.registration import Registration
from iam.shared.application.command_bus import CommandBus

from .dependencies import RegistrationHTTPSettings, get_command_bus, get_registration_http_settings
from .schema import RegistrationStartedResponse, StartEmailPasswordRegistrationBody

CommandBusDep = Annotated[CommandBus, Depends(get_command_bus)]
HTTPSettingsDep = Annotated[
    RegistrationHTTPSettings,
    Depends(get_registration_http_settings),
]


class RegistrationResponse(BaseModel):
    @classmethod
    def from_domain(cls, registration: Registration) -> RegistrationResponse:
        return RegistrationResponse()


def get_command_bus(request: Request) -> CommandBus:
    return request.app.state.command_bus


def create_routes():
    router = APIRouter()

    @router.post(
        "/email-password",
        status_code=status.HTTP_202_ACCEPTED,
        response_model=RegistrationStartedResponse,
    )
    async def start_email_password_registration(
        body: StartEmailPasswordRegistrationBody,
        response: Response,
        bus: CommandBusDep,
        settings: HTTPSettingsDep,
    ):
        result = cast(
            RegistrationStarted,
            await bus.dispatch(
                StartEmailPasswordRegistration(
                    email=str(body.email),
                    password=body.password.get_secret_value(),
                )
            ),
        )

        # set resume cookie
        max_age = max(
            0,
            int((result.expires_at - datetime.now(UTC)).total_seconds()),
        )
        response.set_cookie(
            key=settings.resume_cookie_name,
            value=result.resume_token,
            max_age=max_age,
            expires=result.expires_at,
            path=settings.cookie_path,
            domain=settings.cookie_domain,
            secure=settings.cookie_secure,
            httponly=True,
            samesite=settings.cookie_samesite,
        )

        return RegistrationStartedResponse(
            registration_id=result.registration_id,
            method=result.method,
            step=result.step,
            expires_at=result.expires_at,
        )

    return router
