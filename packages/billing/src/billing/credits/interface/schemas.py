from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from billing.credits.domain.credit_source_type import CreditSourceType


class CreateCreditAccountRequest(BaseModel):
    user_id: str = Field(min_length=1)


class GrantCreditsRequest(BaseModel):
    user_id: str = Field(min_length=1)
    amount: int = Field(gt=0)
    source_type: CreditSourceType = CreditSourceType.SUBSCRIPTION_GRANT
    source_id: str | None = None
    description: str | None = None
    expires_at: datetime | None = None


class PurchaseCreditsRequest(BaseModel):
    user_id: str = Field(min_length=1)
    amount: int = Field(gt=0)
    source_id: str | None = None
    description: str | None = None
    expires_at: datetime | None = None


class ReserveCreditsRequest(BaseModel):
    user_id: str = Field(min_length=1)
    amount: int = Field(gt=0)
    source_id: str | None = None
    description: str | None = None


class ConsumeReservedCreditsRequest(BaseModel):
    user_id: str = Field(min_length=1)
    amount: int = Field(gt=0)
    source_id: str | None = None
    description: str | None = None


class ReleaseReservedCreditsRequest(BaseModel):
    user_id: str = Field(min_length=1)
    amount: int = Field(gt=0)
    source_id: str | None = None
    description: str | None = None


class ExpireCreditsRequest(BaseModel):
    user_id: str = Field(min_length=1)
    description: str | None = None


class CreditBalanceResponse(BaseModel):
    available: int
    reserved: int
    total: int


class CreditGrantResponse(BaseModel):
    id: str
    credit_account_id: str
    amount: int
    remaining: int
    granted_at: datetime
    expires_at: datetime | None
    source_id: str | None


class CreditLedgerEntryResponse(BaseModel):
    id: str
    credit_account_id: str
    delta: int
    balance_after_available: int
    balance_after_reserved: int
    source_type: CreditSourceType
    source_id: str | None
    description: str | None
    occurred_at: datetime


class CreditAccountResponse(BaseModel):
    id: str
    user_id: str
    balance: CreditBalanceResponse
    grants: list[CreditGrantResponse]
    ledger_entries: list[CreditLedgerEntryResponse]


class ErrorResponse(BaseModel):
    code: str
    message: str


CreditOperation = Literal[
    "grant",
    "purchase",
    "reserve",
    "consume_reserved",
    "release_reserved",
    "expire",
]
