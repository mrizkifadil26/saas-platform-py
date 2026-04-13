class BillingError(Exception):
    pass


class InsufficientCredits(BillingError):
    pass


class UnknownPlan(BillingError):
    pass


class IdempotencyConflict(BillingError):
    pass


class InvalidCreditsAmount(BillingError):
    pass
