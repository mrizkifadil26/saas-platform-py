from enum import StrEnum


class CredentialType(StrEnum):
    PASSWORD = "password"
    GOOGLE = "google"


class CredentialStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    # COMPROMISED = "compromised"
