from billing.domain.shared.exceptions import (
    BillingDomainError,
)


class PaygDomainError(BillingDomainError):
    """Base class for all Pay-as-you-go domain errors."""

    pass


class UnknownPaygPack(PaygDomainError):
    """Raised when an unknown Pay-as-you-go pack is requested."""

    pass
