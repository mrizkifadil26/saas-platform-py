# packages/billing/tests/domain/subscription/test_exceptions.py

from billing.domain.subscription.exceptions import (
    DuplicatePeriodGrant,
    InvalidSubscriptionStatus,
    SubscriptionDomainError,
    UnknownPlan,
)


def test_unknown_plan_subclasses_subscription_domain_error():
    assert issubclass(UnknownPlan, SubscriptionDomainError)


def test_invalid_subscription_status_subclasses_subscription_domain_error():
    assert issubclass(
        InvalidSubscriptionStatus, SubscriptionDomainError
    )


def test_duplicate_period_grant_subclasses_subscription_domain_error():
    assert issubclass(
        DuplicatePeriodGrant, SubscriptionDomainError
    )
