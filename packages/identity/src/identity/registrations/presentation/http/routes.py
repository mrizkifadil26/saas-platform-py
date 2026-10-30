from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Request, Response

from identity.registrations.application import (
    BeginEmailRegistration,
    EmailRegistrationStarted,
)

from .dependencies import CommandBusDep, HTTPSettingsDep
from .schema import (
    BeginEmailRegistrationRequest,
    BeginEmailRegistrationResponse,
)


def create_routes():
    router = APIRouter(
        prefix="/registrations",
        tags=[
            "registrations",
        ],
    )

    @router.post("/email")
    async def begin_email_registration(
        body: BeginEmailRegistrationRequest,
        response: Response,
        request: Request,
        bus: CommandBusDep,
        settings: HTTPSettingsDep,
    ) -> BeginEmailRegistrationResponse:
        resume_cookie = settings.registration.cookies.resume
        resume_token = request.cookies.get(
            resume_cookie.name,
        )

        result = cast(
            EmailRegistrationStarted,
            await bus.dispatch(
                BeginEmailRegistration(
                    email=str(body.email),
                    resume_token=resume_token,
                )
            ),
        )

        if result.resume_token is not None:
            response.set_cookie(
                key=resume_cookie.name,
                value=result.resume_token.value,
                httponly=resume_cookie.httponly,
                secure=resume_cookie.secure,
                samesite=resume_cookie.samesite,
                path=resume_cookie.path,
                domain=resume_cookie.domain,
                expires=result.expires_at,
                max_age=result.resume_token_max_age,
            )

        return BeginEmailRegistrationResponse(
            registration_id=str(result.registration_id),
            method=result.method.value,
            step=result.step.value,
            expires_at=result.expires_at,
        )

    return router
