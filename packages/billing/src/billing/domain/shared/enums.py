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
    ADJUST = "adjust"
    REVERSE = "reverse"
    RESERVE = "reserve"
    RELEASE = "release"


class UsageMetric(str, Enum):
    REQUEST = "request"
    TOKEN = "token"
    MINUTE = "minute"
    IMAGE = "image"
    GB = "gb"


class GrantStatus(str, Enum):
    ACTIVE = "active"
    FULLY_CONSUMED = "fully_consumed"
    EXPIRED = "expired"
    REVERSED = "reversed"


class PurchaseStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELED = "canceled"
