from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CreateInvoiceLineRequest(BaseModel):
    description: str = Field(min_length=1, max_length=255)
    quantity: int = Field(gt=0)
    unit_price_amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)


class CreateInvoiceRequest(BaseModel):
    user_id: str
    lines: list[CreateInvoiceLineRequest] = Field(min_length=1)
    auto_issue: bool = False


class InvoiceLineResponse(BaseModel):
    description: str
    quantity: int
    unit_price_amount: Decimal
    currency: str
    total_amount: Decimal


class InvoiceResponse(BaseModel):
    id: str
    user_id: str
    status: str
    total_amount: Decimal
    currency: str
    lines: list[InvoiceLineResponse]
    created_at: datetime
    issued_at: datetime | None
    paid_at: datetime | None
    voided_at: datetime | None
    uncollectible_at: datetime | None
