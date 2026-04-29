from dataclasses import dataclass

from billing.credits.domain.value_objects.credits import Credits
from billing.payg.domain.value_objects.payg_purchase_id import PaygPurchaseId
from billing.shared.domain.domain_event import DomainEvent
from billing.shared.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True)
class PaygPurchaseCreated(DomainEvent):
    purchase_id: PaygPurchaseId
    # TODO: later we should use customer_id instead of user_id, but for now we can use user_id since we don't have customer_id yet
    user_id: UserId
    credits: Credits


@dataclass(frozen=True, slots=True)
class PaygPurchasePaymentSucceeded(DomainEvent):
    purchase_id: PaygPurchaseId
    # TODO: later we should use customer_id instead of user_id, but for now we can use user_id since we don't have customer_id yet
    user_id: UserId


@dataclass(frozen=True, slots=True)
class PaygPurchaseCreditGranted(DomainEvent):
    purchase_id: PaygPurchaseId
    # TODO: later we should use customer_id instead of user_id, but for now we can use user_id since we don't have customer_id yet
    user_id: UserId
    credits: Credits


@dataclass(frozen=True, slots=True)
class PaygPurchasePaymentFailed(DomainEvent):
    purchase_id: PaygPurchaseId
    # TODO: later we should use customer_id instead of user_id, but for now we can use user_id since we don't have customer_id yet
    user_id: UserId
    failure_reason: str


@dataclass(frozen=True, slots=True)
class PaygPurchaseRefunded(DomainEvent):
    purchase_id: PaygPurchaseId
    # TODO: later we should use customer_id instead of user_id, but for now we can use user_id since we don't have customer_id yet
    user_id: UserId
