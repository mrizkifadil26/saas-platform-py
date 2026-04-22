from enum import Enum


class BillingInterval(str, Enum):
    MONTH = "month"
    YEAR = "year"


class SubscriptionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"


class PurchaseStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELED = "canceled"


class CreditSource(str, Enum):
    SUBSCRIPTION = "subscription"
    PAYG = "payg"
    PROMOTION = "promotion"
    ADMIN_ADJUSTMENT = "admin_adjustment"
    REFUND = "refund"
    REVERSAL = "reversal"


class LedgerEntryType(str, Enum):
    GRANT = "grant"
    CONSUME = "consume"
    EXPIRE = "expire"
