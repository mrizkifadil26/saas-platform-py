
from pydantic import BaseModel, Field

from billing.payment.domain.value_objects.payment_method import PaymentMethodType


class PurchasePaygCreditsRequest(BaseModel):
    customer_id: str = Field(..., min_length=1)
    package_code: str = Field(..., min_length=1)
    payment_method: PaymentMethodType = PaymentMethodType.CARD
    payment_provider: str | None = Field(default=None, min_length=1)
    payment_reference: str | None = Field(default=None, min_length=1)
    idempotency_key: str | None = None


class PaygPurchaseResponse(BaseModel):
    purchase_id: str
    user_id: str
    credits: int
    status: str


class PaygPackageResponse(BaseModel):
    code: str
    credits: int
    price: int
    currency: str
