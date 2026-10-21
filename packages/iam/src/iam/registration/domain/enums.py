from _typeshed import StrEnum


class RegistrationMethod(StrEnum):
    EMAIL = "email"
    GOOGLE = "google"
    # OIDC = "oidc"


class RegistrationStatus(StrEnum):
    PENDING = "pending"
    VERIFIED = "verified"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class RegistrationStep(StrEnum):
    EMAIL_CHALLENGE = "email_challenge"
    GOOGLE_CHALLENGE = "google_challenge"
    PASSWORD_SETUP = "password_setup"
    PROFILE_SETUP = "profile_setup"
    COMPLETE = "complete"


class EmailChallengePurpose(StrEnum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    EMAIL_CHANGE = "email_change"
    LOGIN_MAGIC_LINK = "logic_magic_link"
