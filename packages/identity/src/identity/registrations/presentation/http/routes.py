from __future__ import annotations

from typing import cast
from uuid import UUID

from fastapi import APIRouter, Cookie, Response

from identity.registrations.application import (
    BeginEmailRegistration,
    EmailRegistrationStarted,
)
from identity.registrations.application.commands import (
    SetRegistrationPassword,
    VerifyRegistrationEmailLink,
    VerifyRegistrationEmailOtp,
)
from identity.registrations.application.dto import EmailVerificationResult, PasswordSet
from identity.registrations.domain.value_objects import RegistrationId

from .dependencies import ClockDep, CommandBusDep, HTTPSettingsDep, RequestContextDep
from .schemas import (
    BeginEmailRegistrationRequest,
    BeginEmailRegistrationResponse,
    SetRegistrationPasswordRequest,
    SetRegistrationPasswordResponse,
    VerifyEmailRegistrationLinkRequest,
    VerifyEmailRegistrationOtpRequest,
    VerifyEmailRegistrationResponse,
)


def create_routes():
    router = APIRouter(
        prefix="/registrations",
        tags=[
            "registrations",
        ],
    )

    @router.post("/start")
    async def begin_email_registration(
        body: BeginEmailRegistrationRequest,
        response: Response,
        bus: CommandBusDep,
        clock: ClockDep,
        settings: HTTPSettingsDep,
        context: RequestContextDep,
    ) -> BeginEmailRegistrationResponse:
        result = cast(
            EmailRegistrationStarted,
            await bus.dispatch(
                BeginEmailRegistration(
                    email=str(body.email),
                ),
                context=context,
            ),
        )

        cookie = settings.registration.cookies.session
        remaining = result.expires_at - clock.now()
        max_age = max(0, int(remaining.total_seconds()))

        response.set_cookie(
            key=cookie.name,
            value=str(result.registration_id),
            httponly=cookie.httponly,
            secure=cookie.secure,
            samesite=cookie.samesite,
            path=cookie.path,
            domain=cookie.domain,
            expires=result.expires_at,
            max_age=max_age,
        )

        return BeginEmailRegistrationResponse(
            method=result.method.value,
            step=result.step.value,
            expires_at=result.expires_at,
        )

    @router.post("/verify/link")
    async def verify_registration_link(
        body: VerifyEmailRegistrationLinkRequest,
        bus: CommandBusDep,
        context: RequestContextDep,
        registration_id: str | None = Cookie(
            default=None,
            alias="registration_session",
        ),
    ) -> VerifyEmailRegistrationResponse:
        if registration_id is None:
            # raise RegistrationSessionRequired()
            raise

        result = cast(
            EmailVerificationResult,
            await bus.dispatch(
                VerifyRegistrationEmailLink(
                    registration_id=RegistrationId(UUID(registration_id)),
                    challenge_token=body.token,
                ),
                context=context,
            ),
        )

        return VerifyEmailRegistrationResponse(
            method=result.registration.method.value,
            step=result.registration.step.value,
            expires_at=result.registration.expires_at,
        )

    @router.post("/verify/otp")
    async def verify_registration_otp(
        body: VerifyEmailRegistrationOtpRequest,
        bus: CommandBusDep,
        context: RequestContextDep,
        registration_id: str | None = Cookie(
            default=None,
            alias="registration_session",
        ),
    ) -> VerifyEmailRegistrationResponse:
        if registration_id is None:
            # raise RegistrationSessionRequired()
            raise

        result = cast(
            EmailVerificationResult,
            await bus.dispatch(
                VerifyRegistrationEmailOtp(
                    registration_id=RegistrationId(UUID(registration_id)),
                    otp_code=body.code,
                ),
                context=context,
            ),
        )

        return VerifyEmailRegistrationResponse(
            method=result.registration.method.value,
            step=result.registration.step.value,
            expires_at=result.registration.expires_at,
        )

    @router.post("/password")
    async def set_password(
        body: SetRegistrationPasswordRequest,
        bus: CommandBusDep,
        context: RequestContextDep,
        registration_id: str | None = Cookie(
            default=None,
            alias="registration_session",
        ),
    ) -> SetRegistrationPasswordResponse:
        if registration_id is None:
            # raise RegistrationSessionRequired()
            raise

        result = cast(
            PasswordSet,
            await bus.dispatch(
                SetRegistrationPassword(
                    registration_id=RegistrationId(UUID(registration_id)),
                    password=body.password,
                ),
                context=context,
            ),
        )

        return SetRegistrationPasswordResponse(
            status=result.registration.status,
        )

    return router
