# packages/billing/tests/domain/credits/test_policies.py

from datetime import timedelta
from typing import cast

from billing.domain.credits.entities import CreditGrant
from billing.domain.credits.policies import grant_priority
from billing.domain.credits.value_objects import (
    Credits,
    GrantId,
)
from billing.domain.shared.enums import CreditSource


def make_credit_grant(
    *,
    user_id,
    now,
    source: CreditSource,
    expires_at,
    created_at=None,
):
    return CreditGrant(
        grant_id=GrantId.new(),
        user_id=user_id,
        granted_credits=Credits(100),
        remaining_credits=Credits(100),
        source=source,
        created_at=created_at or now,
        expires_at=expires_at,
        metadata={},
    )


def test_grant_priority_sorts_subscription_before_payg(
    now,
    user_id,
):
    subscription = make_credit_grant(
        user_id=user_id,
        now=now,
        source="subscription",
        expires_at=now + timedelta(days=1),
    )

    payg = make_credit_grant(
        user_id=user_id,
        now=now,
        source="payg",
        expires_at=now + timedelta(days=1),
    )

    ordered = sorted(
        [payg, subscription], key=grant_priority
    )

    assert ordered == [subscription, payg]


def test_grant_priority_sorts_payg_before_promotion(
    now,
    user_id,
):
    payg = make_credit_grant(
        user_id=user_id,
        now=now,
        source="payg",
        expires_at=now + timedelta(days=1),
    )
    promotion = make_credit_grant(
        user_id=user_id,
        now=now,
        source="promotion",
        expires_at=now + timedelta(days=1),
    )

    ordered = sorted([promotion, payg], key=grant_priority)

    assert ordered == [payg, promotion]


def test_grant_priority_sorts_unknown_source_last(
    now, user_id
):
    unknown = make_credit_grant(
        user_id=user_id,
        now=now,
        source=cast(CreditSource, "mystery"),
        expires_at=now + timedelta(days=1),
    )

    subscription = make_credit_grant(
        user_id=user_id,
        now=now,
        source="subscription",
        expires_at=now + timedelta(days=1),
    )

    ordered = sorted(
        [unknown, subscription], key=grant_priority
    )

    assert ordered == [subscription, unknown]


def test_grant_priority_prefers_earlier_expires_at(
    now, user_id
):
    earlier = make_credit_grant(
        user_id=user_id,
        now=now,
        source="payg",
        expires_at=now + timedelta(days=1),
    )
    later = make_credit_grant(
        user_id=user_id,
        now=now,
        source="payg",
        expires_at=now + timedelta(days=10),
    )

    ordered = sorted([later, earlier], key=grant_priority)

    assert ordered == [earlier, later]


def test_grant_priority_uses_datetime_max_when_no_expiry(
    now, user_id
):
    no_expiry = make_credit_grant(
        user_id=user_id,
        now=now,
        source="payg",
        expires_at=None,
    )
    expires = make_credit_grant(
        user_id=user_id,
        now=now,
        source="payg",
        expires_at=now + timedelta(days=1),
    )

    ordered = sorted(
        [no_expiry, expires], key=grant_priority
    )

    assert ordered == [expires, no_expiry]


def test_grant_priority_breaks_ties_with_earlier_created_at(
    now,
    user_id,
):
    earlier = make_credit_grant(
        user_id=user_id,
        now=now,
        source="payg",
        expires_at=now + timedelta(days=1),
        created_at=now,
    )
    later = make_credit_grant(
        user_id=user_id,
        now=now,
        source="payg",
        expires_at=now + timedelta(days=1),
        created_at=now + timedelta(minutes=1),
    )

    ordered = sorted([later, earlier], key=grant_priority)

    assert ordered == [earlier, later]
