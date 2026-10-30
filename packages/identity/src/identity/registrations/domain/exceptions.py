from typing import Any

from identity.shared.kernel.exceptions import DomainError


class RegistrationError(DomainError):
    """Base exception for registration domain errors."""

    code = "registration_error"

    def __init__(self, **context: Any) -> None:
        super().__init__()
        self.context = context


class RegistrationEmailError(RegistrationError):
    """Base exception for registration email state errors."""


class RegistrationEmailNotSetError(RegistrationEmailError):
    code = "registration_email_not_set"


class RegistrationEmailNotVerifiedError(RegistrationEmailError):
    code = "registration_email_not_verified"


class RegistrationEmailAlreadyVerifiedError(RegistrationEmailError):
    code = "registration_email_already_verified"


class RegistrationPasswordError(RegistrationError):
    """Base exception for registration password state errors."""


class RegistrationPasswordNotSetError(RegistrationPasswordError):
    code = "registration_password_not_set"


class RegistrationPasswordAlreadySetError(RegistrationPasswordError):
    code = "registration_password_already_set"


class RegistrationUserError(RegistrationError):
    """Registration user-assignment error."""


class RegistrationUserAlreadyAssignedError(RegistrationUserError):
    code = "registration_user_already_assigned"


class RegistrationWorkflowError(DomainError):
    """Base error for registration workflow."""

    code = "registration_workflow_error"

    def __init__(self, **context: Any) -> None:
        super().__init__()
        self.context = context


class RegistrationNotFoundError(RegistrationWorkflowError):
    code = "registration_not_found"


class RegistrationNotPendingError(RegistrationWorkflowError):
    code = "registration_not_pending"


class RegistrationAlreadyCompletedError(RegistrationWorkflowError):
    code = "registration_already_completed"


class RegistrationExpiredError(RegistrationWorkflowError):
    code = "registration_expired"


class RegistrationCancelledError(RegistrationWorkflowError):
    code = "registration_cancelled"


class RegistrationAlreadyCancelledError(RegistrationWorkflowError):
    code = "registration_already_cancelled"


class RegistrationNotCancellableError(RegistrationWorkflowError):
    code = "registration_not_cancellable"


class RegistrationNotCompletableError(RegistrationWorkflowError):
    code = "registration_not_completable"


class RegistrationStepError(RegistrationWorkflowError):
    code = "registration_step_error"

    def __init__(self, step: str, **context: Any) -> None:
        super().__init__(step=step, **context)


class RegistrationResumeError(RegistrationWorkflowError):
    """Resume-token/workflow access error."""


class InvalidRegistrationResumeTokenError(RegistrationResumeError):
    code = "invalid_registration_resume_token"


class EmailChallengeError(DomainError):
    """Base error for email challenge domain."""

    code = "email_challenge_error"

    def __init__(self, **context: Any) -> None:
        super().__init__()
        self.context = context


class EmailChallengeExpiredError(EmailChallengeError):
    code = "email_challenge_expired"


class EmailChallengeRevokedError(EmailChallengeError):
    code = "email_challenge_revoked"


class EmailChallengeAlreadyCompletedError(EmailChallengeError):
    code = "email_challenge_already_completed"


class InvalidEmailChallengeTokenError(EmailChallengeError):
    code = "invalid_email_challenge_token"
