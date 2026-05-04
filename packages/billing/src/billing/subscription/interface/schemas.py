from datetime import datetime

from pydantic import BaseModel, Field


class CreateSubscriptionItemRequest(BaseModel):
    item_id: str = Field(..., min_length=1)
    product_code: str = Field(..., min_length=1)
    feature_code: str = Field(..., min_length=1)
    quantity: int = Field(default=1, gt=0)


class CreateSubscriptionRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    plan_code: str = Field(..., min_length=1)
    period_start: datetime
    period_end: datetime
    items: list[CreateSubscriptionItemRequest] = Field(default_factory=list)
    provider_subscription_id: str | None = None
    trial: bool = False


class SubscriptionItemResponse(BaseModel):
    item_id: str
    product_code: str
    feature_code: str
    quantity: int


class SubscriptionResponse(BaseModel):
    subscription_id: str
    user_id: str
    plan_code: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    provider_subscription_id: str | None
    items: list[SubscriptionItemResponse]
