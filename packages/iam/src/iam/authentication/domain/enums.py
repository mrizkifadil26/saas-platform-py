from enum import StrEnum


class AuthenticationStatus(StrEnum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"
    LOCKED_OUT = "locked_out"


class CredentialStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    COMPROMISED = "compromised"
