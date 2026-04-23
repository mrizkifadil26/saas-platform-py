from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GetSubscriptionQuery:
    subscription_id: str
