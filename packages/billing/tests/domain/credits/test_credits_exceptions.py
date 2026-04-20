# packages/billing/tests/domain/credits/test_exceptions.py

from billing.domain.credits.exceptions import (
    CreditsDomainError,
    InsufficientCredits,
    InvalidCreditsAmount,
)


def test_insufficient_credits_subclasses_credits_domain_error():
    assert issubclass(
        InsufficientCredits, CreditsDomainError
    )


def test_invalid_credits_amount_subclasses_credits_domain_error():
    assert issubclass(
        InvalidCreditsAmount, CreditsDomainError
    )
