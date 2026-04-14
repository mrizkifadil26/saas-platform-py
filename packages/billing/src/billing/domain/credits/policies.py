from datetime import datetime

from billing.domain.credits.models import CreditGrant


def is_grant_active(
    grant: CreditGrant,
    now: datetime,
) -> bool:
    if (
        grant.expires_at is not None
        and grant.expires_at < now
    ):
        return False

    if int(grant.remaining_credits) <= 0:
        return False

    return True


def grant_priority(
    grant: CreditGrant,
) -> tuple[int, datetime, datetime]:
    source_rank = {
        "subscription": 0,
        "payg": 1,
        "promotion": 2,
        "compensation": 3,
    }.get(grant.source, 99)

    expiry_sort = grant.expires_at or datetime.max
    return (source_rank, expiry_sort, grant.created_at)
