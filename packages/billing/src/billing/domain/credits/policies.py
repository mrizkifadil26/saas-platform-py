from datetime import datetime

from billing.domain.credits.models import CreditGrant


def is_grant_active(
    grant: CreditGrant,
    now: datetime,
) -> bool: ...


def grant_priority(grant: CreditGrant) -> tuple[int, datetime, datetime]: ...
