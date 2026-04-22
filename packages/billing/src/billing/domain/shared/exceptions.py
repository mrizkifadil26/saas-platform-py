class DomainError(Exception):
    """Base exception for all domain-level errors."""


class ValidationError(DomainError):
    """Exception raised for validation errors in the domain."""


class NotFoundError(DomainError):
    """Exception raised when an entity is not found in the domain."""
