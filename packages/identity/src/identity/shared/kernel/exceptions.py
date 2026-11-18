class DomainError(Exception):
    """Base domain exception."""


class ValidationError(DomainError):
    """Raised when a domain rule is violated."""


class NotFoundError(DomainError):
    """Raised when an entity does not exist."""


class ConflictError(DomainError):
    """Raised when an operation conflicts with current state."""


class UnauthorizedError(DomainError):
    """Raised when identity is missing or invalid."""


class ForbiddenError(DomainError):
    """Raised when identity exists but lacks permission."""
