from dataclasses import dataclass

from .enums import RegistrationMethod, RegistrationStep
from .exceptions import (
    RegistrationEmailNotVerifiedError,
    RegistrationNotCompletableError,
    RegistrationPasswordAlreadySetError,
    RegistrationPasswordNotSetError,
    RegistrationStepError,
)


@dataclass(frozen=True, slots=True)
class RegistrationPolicy:
    def initial_step(
        self,
        *,
        method: RegistrationMethod,
    ) -> RegistrationStep:
        match method:
            case RegistrationMethod.EMAIL:
                return RegistrationStep.EMAIL_CHALLENGE
            case RegistrationMethod.GOOGLE:
                return RegistrationStep.GOOGLE_CHALLENGE

        raise ValueError(f"Unsupported registration method: {method}")

    def ensure_can_verify_email(
        self,
        *,
        method: RegistrationMethod,
        step: RegistrationStep,
    ) -> None:
        if method is not RegistrationMethod.EMAIL:
            raise RegistrationStepError(step=step)

        if step is not RegistrationStep.EMAIL_CHALLENGE:
            raise RegistrationStepError(step=step)

    def ensure_can_set_password(
        self,
        *,
        method: RegistrationMethod,
        step: RegistrationStep,
        email_verified: bool,
        password_configured: bool,
    ) -> None:
        if method is not RegistrationMethod.EMAIL:
            raise RegistrationStepError(step=step)

        if step is not RegistrationStep.PASSWORD_SETUP:
            raise RegistrationStepError(step=step)

        if not email_verified:
            raise RegistrationEmailNotVerifiedError()

        if password_configured:
            # This is arguably better enforced by Registration itself.
            raise RegistrationPasswordAlreadySetError()

    def ensure_can_complete(
        self,
        *,
        method: RegistrationMethod,
        step: RegistrationStep,
        email_verified: bool,
        password_configured: bool,
    ) -> None:
        if step is not RegistrationStep.COMPLETE:
            raise RegistrationNotCompletableError()

        match method:
            case RegistrationMethod.EMAIL:
                if not email_verified:
                    raise RegistrationEmailNotVerifiedError()

                if not password_configured:
                    raise RegistrationPasswordNotSetError()

            case RegistrationMethod.GOOGLE:
                pass
