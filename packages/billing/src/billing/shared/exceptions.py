class BillingError(Exception):
    """Base class for all billing-related errors."""

    pass


class DomainError(BillingError):
    """Base exception for all domain-level errors."""

    pass


class ApplicationError(BillingError):
    """Base exception for all application-level errors."""

    pass


class InfrastructureError(BillingError):
    """Base exception for all infrastructure-level errors."""

    pass


class ValidationError(DomainError):
    """Exception raised for validation errors in the domain."""

    pass


class NotFoundError(ApplicationError):
    """Exception raised when an entity is not found in the domain."""

    pass


class ConflictError(ApplicationError):
    """Exception raised when there is a conflict in the application."""

    pass


class ExternalServiceError(InfrastructureError):
    """Exception raised when an external service call fails."""

    pass
