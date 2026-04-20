from datetime import datetime

from billing.domain.credits.entities import CreditGrant


def grant_priority(
    grant: CreditGrant,
) -> tuple[int, datetime, datetime]:
    source_rank = {
        "subscription": 0,
        "payg": 1,
        "promotion": 2,
        "compensation": 3,
    }.get(grant.source, 99)

    expiry_sort = grant.expires_at or datetime.max.replace(
        tzinfo=grant.created_at.tzinfo
    )
    return (source_rank, expiry_sort, grant.created_at)
