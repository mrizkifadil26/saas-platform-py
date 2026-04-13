from datetime import datetime, timezone
from typing import Literal, NewType

Credits = NewType("Credits", int)
RequestId = NewType("RequestId", str)
PlanCode = NewType("PlanCode", str)
UserId = NewType("UserId", str)
GrantId = NewType("GrantId", str)
ConsumptionId = NewType("ConsumptionId", str)
SubscriptionId = NewType("SubscriptionId", str)

CreditSource = Literal["payg", "subscription"]
SubscriptionStatus = Literal["active", "past_due", "canceled"]


def utc_now() -> datetime:
    """Timezone-aware UTC datetime"""
    return datetime.now(timezone.utc)
