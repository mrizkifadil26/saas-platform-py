from http import HTTPStatus

from identity.registrations.domain.exceptions import (
    EmailChallengeAlreadyCompletedError,
    EmailChallengeExpiredError,
    EmailChallengeRevokedError,
    InvalidEmailChallengeTokenError,
    RegistrationAlreadyCancelledError,
    RegistrationAlreadyCompletedError,
    RegistrationCancelledError,
    RegistrationEmailAlreadyVerifiedError,
    RegistrationEmailNotSetError,
    RegistrationEmailNotVerifiedError,
    RegistrationExpiredError,
    RegistrationNotCancellableError,
    RegistrationNotCompletableError,
    RegistrationNotFoundError,
    RegistrationPasswordAlreadySetError,
    RegistrationPasswordNotSetError,
    RegistrationStepError,
)
from identity.shared.infrastructure.http.errors import HTTPError

REGISTRATION_ERRORS: dict[type[Exception], HTTPError] = {
    RegistrationNotFoundError: HTTPError(
        status=HTTPStatus.NOT_FOUND,
        code="registration_not_found",
        message="Registration was not found.",
    ),
    RegistrationAlreadyCompletedError: HTTPError(
        status=HTTPStatus.CONFLICT,
        code="registration_already_completed",
        message="Registration has already been completed.",
    ),
    RegistrationExpiredError: HTTPError(
        status=HTTPStatus.CONFLICT,
        code="registration_expired",
        message="Registration has expired.",
    ),
    RegistrationCancelledError: HTTPError(
        status=HTTPStatus.CONFLICT,
        code="registration_cancelled",
        message="Registration has been cancelled.",
    ),
    RegistrationAlreadyCancelledError: HTTPError(
        status=HTTPStatus.CONFLICT,
        code="registration_already_cancelled",
        message="Registration has already been cancelled.",
    ),
    RegistrationNotCancellableError: HTTPError(
        status=HTTPStatus.CONFLICT,
        code="registration_not_cancellable",
        message="Registration cannot be cancelled.",
    ),
    RegistrationNotCompletableError: HTTPError(
        status=HTTPStatus.CONFLICT,
        code="registration_not_completable",
        message="Registration cannot be completed.",
    ),
    RegistrationStepError: HTTPError(
        status=HTTPStatus.CONFLICT,
        code="registration_step_error",
        message="Registration cannot perform this step.",
    ),
    RegistrationEmailNotSetError: HTTPError(
        status=HTTPStatus.CONFLICT,
        code="registration_email_not_set",
        message="Registration does not have an email address.",
    ),
    RegistrationEmailNotVerifiedError: HTTPError(
        status=HTTPStatus.CONFLICT,
        code="registration_email_not_verified",
        message="Registration email has not been verified.",
    ),
    RegistrationEmailAlreadyVerifiedError: HTTPError(
        status=HTTPStatus.CONFLICT,
        code="registration_email_already_verified",
        message="Registration email has already been verified.",
    ),
    RegistrationPasswordNotSetError: HTTPError(
        status=HTTPStatus.CONFLICT,
        code="registration_password_not_set",
        message="Registration password has not been set.",
    ),
    RegistrationPasswordAlreadySetError: HTTPError(
        status=HTTPStatus.CONFLICT,
        code="registration_password_already_set",
        message="Registration password has already been set.",
    ),
    EmailChallengeExpiredError: HTTPError(
        status=HTTPStatus.CONFLICT,
        code="email_challenge_expired",
        message="Email verification has expired.",
    ),
    EmailChallengeRevokedError: HTTPError(
        status=HTTPStatus.CONFLICT,
        code="email_challenge_revoked",
        message="Email verification is no longer valid.",
    ),
    EmailChallengeAlreadyCompletedError: HTTPError(
        status=HTTPStatus.CONFLICT,
        code="email_challenge_already_completed",
        message="Email verification has already been completed.",
    ),
    InvalidEmailChallengeTokenError: HTTPError(
        status=HTTPStatus.BAD_REQUEST,
        code="invalid_email_challenge_token",
        message="The email verification token is invalid.",
    ),
}
