class PasswordPolicyViolation(ValueError):
    """Raised when a password doesn't satisfy the password policy."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
