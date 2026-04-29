from enum import StrEnum


class PaymentStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"

    def can_start_processing(self) -> bool:
        return self is PaymentStatus.PENDING

    def can_succeed(self) -> bool:
        return self is PaymentStatus.PROCESSING

    def can_fail(self) -> bool:
        return self in {
            PaymentStatus.PENDING,
            PaymentStatus.PROCESSING,
        }

    def can_cancel(self) -> bool:
        return self is PaymentStatus.PENDING

    def can_refund(self) -> bool:
        return self is PaymentStatus.SUCCEEDED
