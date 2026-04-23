class DatabaseError(Exception):
    """Base database error."""


class DatabaseConnectionError(DatabaseError):
    """Raised when DB connection fails."""


class TransactionError(DatabaseError):
    """Raised when transaction fails."""


class RepositoryError(DatabaseError):
    """Raised for repository-level issues."""
