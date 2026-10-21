from iam.shared.kernel.exceptions import DomainError


class RegistrationError(DomainError):
    """Base exception for identity module"""


class EmailChallengeError(DomainError): ...


# class UserEmailVerificationBlockedError(
#     InvalidUserStateError,
# ):
#     """Raised when email verification is blocked."""


# class UserEmailAlreadyVerifiedError(
#     InvalidUserStateError,
# ):
#     """Raised when an already verified email is verified again."""


class EmailVerificationAlreadyVerifiedError(EmailChallengeError):
    def __init__(self) -> None:
        super().__init__(
            "Email verification has already been verified.",
        )


class EmailVerificationExpiredError(EmailChallengeError):
    def __init__(self) -> None:
        super().__init__(
            "Email verification has expired.",
        )


class InvalidEmailVerificationTokenError(EmailChallengeError): ...


class RegistrationAlreadyCompletedError(RegistrationError): ...


class RegistrationNotCancellableError(RegistrationError): ...


class RegistrationExpiredError(RegistrationError): ...


class RegistrationStepError(RegistrationError): ...


class RegistrationNotCompletableError(RegistrationError): ...


class RegistrationAlreadyCancelledError(RegistrationError): ...


class RegistrationEmailAlreadyVerifiedError(RegistrationError): ...


class RegistrationNotFoundError(RegistrationError): ...


class RegistrationEmailNotVerifiedError(RegistrationError): ...


class RegistrationPasswordNotSetError(RegistrationError): ...


class RegistrationPasswordAlreadySetError(RegistrationError): ...


class RegistrationCancelledError(RegistrationError): ...


class RegistrationEmailNotSetError(RegistrationError): ...


class EmailChallengeRevokedError(RegistrationError): ...
