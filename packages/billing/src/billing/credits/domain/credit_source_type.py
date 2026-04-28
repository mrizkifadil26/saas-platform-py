from __future__ import annotations

from enum import StrEnum


class CreditSourceType(StrEnum):
    SUBSCRIPTION_GRANT = "subscription_grant"
    PURCHASE = "purchase"
    # ADMIN_ADJUSTMENT = "admin_adjustment"
    # REFUND = "refund"
    # EXPIRATION = "expiration"
    USAGE_CONSUMPTION = "usage_consumption"
    RESERVATION = "reservation"
    RESERVATION_RELEASE = "reservation_release"