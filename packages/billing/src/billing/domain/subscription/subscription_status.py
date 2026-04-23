from enum import StrEnum


class SubscriptionStatus(StrEnum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    PAUSED = "paused"
    CANCELED = "canceled"
    EXPIRED = "expired"

    @property
    def is_activeish(self) -> bool:
        """Returns True if the subscription is in an active-like state."""
        return self in {
            SubscriptionStatus.TRIALING,
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.PAST_DUE,
        }

    @property
    def is_terminal(self) -> bool:
        """Returns True if the subscription is in a terminal state."""
        return self in {
            SubscriptionStatus.CANCELED,
            SubscriptionStatus.EXPIRED,
        }

    def can_renew(self) -> bool:
        """Returns True if the subscription can be renewed."""
        return self in {
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.PAST_DUE,
        }
