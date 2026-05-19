from enum import StrEnum


class AuthenticationOutcome(StrEnum):
    SUCCESS = "success"
    DENIED = "denied"
    LOCKED_OUT = "locked_out"


class CredentialType(StrEnum):
    PASSWORD = "password"


class CredentialStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    COMPROMISED = "compromised"


class AuthenticationDenialReason(StrEnum):
    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_DISABLED = "account_disabled"
    ACCOUNT_LOCKED = "account_locked"
    EMAIL_NOT_VERIFIED = "email_not_verified"
    UNKNOWN_IDENTITY = "unknown_identity"
