from uuid import UUID


class RegistrationError(Exception):
    """Base error for the registration workflow."""


class RegistrationNotPendingError(RegistrationError):
    def __init__(self, registration_id: UUID) -> None:
        super().__init__(
            f"Registration {registration_id} is not pending.",
        )


class RegistrationCancelledError(RegistrationError):
    def __init__(self, registration_id: UUID) -> None:
        super().__init__(
            f"Registration {registration_id} has been cancelled.",
        )


class RegistrationExpiredError(RegistrationError):
    def __init__(self, registration_id: UUID) -> None:
        super().__init__(
            f"Registration {registration_id} has expired.",
        )


class RegistrationEmailNotVerifiedError(RegistrationError):
    def __init__(self, registration_id: UUID) -> None:
        super().__init__(
            f"Registration {registration_id} does not have a verified email.",
        )


class RegistrationEmailAlreadyRegisteredError(RegistrationError):
    def __init__(self) -> None:
        super().__init__(
            "The email address is already registered.",
        )


class RegistrationPasswordNotSetError(RegistrationError):
    def __init__(self, registration_id: UUID) -> None:
        super().__init__(
            f"Registration {registration_id} does not have a configured password.",
        )


class RegistrationAlreadyCompletedError(RegistrationError):
    def __init__(self, registration_id: UUID) -> None:
        super().__init__(
            f"Registration {registration_id} has already been completed.",
        )


class RegistrationNotCompletableError(RegistrationError):
    def __init__(self, registration_id: UUID) -> None:
        super().__init__(
            f"Registration {registration_id} is not ready to be completed.",
        )


class RegistrationResumeTokenRequiredError(RegistrationError):
    def __init__(self) -> None:
        super().__init__(
            "A registration resume token is required to continue this registration.",
        )


class RegistrationResumeTokenInvalidError(RegistrationError):
    def __init__(self) -> None:
        super().__init__(
            "The registration resume token is invalid.",
        )


class EmailChallengeError(RegistrationError):
    """Base error for email verification challenges."""


class EmailChallengeNotFoundError(EmailChallengeError):
    def __init__(self, challenge_id: UUID) -> None:
        super().__init__(
            f"Email challenge {challenge_id} was not found.",
        )


class EmailChallengeExpiredError(EmailChallengeError):
    def __init__(self, challenge_id: UUID) -> None:
        super().__init__(
            f"Email challenge {challenge_id} has expired.",
        )


class EmailChallengeAlreadyVerifiedError(EmailChallengeError):
    def __init__(self, challenge_id: UUID) -> None:
        super().__init__(
            f"Email challenge {challenge_id} has already been verified.",
        )


class EmailChallengeAlreadyCompletedError(EmailChallengeError):
    def __init__(self, challenge_id: UUID) -> None:
        super().__init__(
            f"Email challenge {challenge_id} has already been completed.",
        )


class EmailChallengeInvalidTokenError(EmailChallengeError):
    def __init__(self) -> None:
        super().__init__(
            "The email verification token is invalid.",
        )
