from enum import StrEnum


class PaygPurchaseStatus(StrEnum):
    PENDING = "pending"
    PAYMENT_SUCCEEDED = "payment_succeeded"
    CREDITS_GRANTED = "credits_granted"
    FAILED = "failed"
    REFUNDED = "refunded"
    # CANCELED = "canceled"

    def can_mark_payment_succeeded(self) -> bool:
        return self is PaygPurchaseStatus.PENDING

    def can_mark_credits_granted(self) -> bool:
        return self is PaygPurchaseStatus.PAYMENT_SUCCEEDED

    def can_fail(self) -> bool:
        return self in {
            PaygPurchaseStatus.PENDING,
            PaygPurchaseStatus.PAYMENT_SUCCEEDED,
        }

    def can_refund(self) -> bool:
        return self is PaygPurchaseStatus.CREDITS_GRANTED
