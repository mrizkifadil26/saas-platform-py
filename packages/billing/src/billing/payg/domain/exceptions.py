from billing.shared.exceptions import DomainError


class PaygDomainError(DomainError):
    """Base class for all Pay-as-you-go domain errors."""

    pass


class UnknownPaygPack(PaygDomainError):
    """Raised when an unknown Pay-as-you-go pack is requested."""

    pass


class PurchaseStateError(PaygDomainError):
    """Raised when an invalid state transition is attempted on a purchase."""

    pass


class InvalidMoney(PaygDomainError):
    """Raised when an invalid money amount is used in a purchase."""

    pass
