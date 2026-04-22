from billing.domain.credits.entities import CreditGrant
from billing.domain.credits.value_objects import Credits
from billing.domain.shared.enums import CreditSource


def sort_spendable_grants(
    grants: list[CreditGrant], at
) -> list[CreditGrant]:
    """
    Consumption priority:
    1. active only
    2. earliest expiry first
    3. subscription before payg when same expiry
    4. oldest grant first
    """
    active = [
        grant for grant in grants if grant.is_active_at(at)
    ]

    def priority(grant: CreditGrant) -> tuple:
        expiry_rank = grant.expires_at is None
        source_rank = (
            0
            if grant.source == CreditSource.SUBSCRIPTION
            else 1
        )
        expiry_value = grant.expires_at
        return (
            expiry_rank,
            expiry_value,
            source_rank,
            grant.granted_at,
        )

    return sorted(active, key=priority)


def total_available_credits(
    grants: list[CreditGrant], at
) -> Credits:
    total = 0
    for grant in grants:
        if grant.is_active_at(at):
            total += int(grant.available_credits)

    return Credits(total)
