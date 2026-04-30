from dataclasses import dataclass

from billing.payg.domain.value_objects.payg_purchase_id import PaygPurchaseId
from billing.payment.domain.value_objects.payment_method import PaymentMethod
from billing.shared.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True)
class PurchasePaygCreditsCommand:
    # TODO: later we should replace it with customer_id
    user_id: UserId
    package_code: str
    payment_method: PaymentMethod
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class MarkPaygPaymentSucceededCommand:
    purchase_id: PaygPurchaseId


@dataclass(frozen=True, slots=True)
class MarkPaygPaymentFailedCommand:
    purchase_id: PaygPurchaseId
    reason: str


@dataclass(frozen=True, slots=True)
class GrantPaygCreditsCommand:
    purchase_id: PaygPurchaseId
