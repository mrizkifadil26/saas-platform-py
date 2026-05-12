from iam.identity.domain.value_objects import UserId


class UserAlreadyExistsError(Exception):
    """Raised when a user with the specified email already exists."""

    def __init__(self, email: str) -> None:
        super().__init__(f"User already exists: {email}")


class UserNotFoundError(Exception):
    """Raised when a user with the specified identifier does not exist."""

    def __init__(self, user_id: UserId) -> None:
        super().__init__(f"User not found: {user_id.value}")


class UserNotFoundByEmailError(Exception):
    """Raised when a user with the specified email does not exist."""

    def __init__(self, email: str) -> None:
        super().__init__(f"User not found with email: {email}")


class InvalidPasswordError(Exception):
    """Raised when a provided password does not meet security requirements."""
