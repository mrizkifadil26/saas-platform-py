from iam.shared.domain.exceptions import DomainError


class UserAlreadyExists(DomainError):
    """Raised when trying to register a user with an email that already exists."""
