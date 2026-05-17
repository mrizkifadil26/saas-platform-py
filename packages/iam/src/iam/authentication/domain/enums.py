from enum import StrEnum


class AuthenticationStatus(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    LOCKED_OUT = "locked_out"


class CredentialType(StrEnum):
    PASSWORD = "password"


class CredentialStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    COMPROMISED = "compromised"


class AuthenticationFailureReason(StrEnum):
    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_DISABLED = "account_disabled"
    ACCOUNT_LOCKED = "account_locked"
    MFA_REQUIRED = "mfa_required"
    MFA_FAILED = "mfa_failed"
    EMAIL_NOT_VERIFIED = "email_not_verified"
    UNKNOWN_IDENTITY = "unknown_identity"