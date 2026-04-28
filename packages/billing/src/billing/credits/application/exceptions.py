from billing.shared.exceptions import ApplicationError


class CreditApplicationError(ApplicationError):
    """Base exception for credit application errors."""


class CreditAccountNotFoundError(CreditApplicationError):
    """Raised when a credit account cannot be found."""


class CreditAccountAlreadyExistsError(CreditApplicationError):
    """Raised when creating a duplicate credit account."""


class CreditOperationAlreadyProcessedError(CreditApplicationError):
    """Raised when a credit operation was already processed."""
