from __future__ import annotations

from pydantic import BaseModel


class PaymentSucceededEvent(BaseModel):
    purchase_id: str
    amount: int
    currency: str
