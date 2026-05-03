from __future__ import annotations

from billing.credits.domain.value_objects.credits import Credits
from billing.payg.domain.payg_purchase import PaygPurchase
from billing.payg.domain.payg_purchase_status import PaygPurchaseStatus
from billing.payg.domain.value_objects.pack_code import PackCode
from billing.payg.domain.value_objects.payg_purchase_id import PaygPurchaseId
from billing.payg.infrastructure.sqlalchemy.models import PaygPurchaseModel
from billing.shared.domain.value_objects.currency import Currency
from billing.shared.domain.value_objects.money import Money
from billing.shared.domain.value_objects.user_id import UserId


class PaygPurchaseORMMapper:
    @staticmethod
    def from_model(model: PaygPurchaseModel) -> PaygPurchase:
        return PaygPurchase(
            id=PaygPurchaseId(model.id),
            user_id=UserId(model.user_id),
            pack_code=PackCode(model.pack_code),
            credits=Credits(model.credits),
            price=Money(
                amount=model.price_amount,
                currency=Currency(model.price_currency),
            ),
            expires_in_days=model.expires_in_days,
            status=PaygPurchaseStatus(model.status),
            created_at=model.created_at,
            paid_at=model.paid_at,
            credits_granted_at=model.credits_granted_at,
            failed_at=model.failed_at,
            refunded_at=model.refunded_at,
            failure_reason=model.failure_reason,
        )

    @staticmethod
    def to_model(domain: PaygPurchase) -> PaygPurchaseModel:
        return PaygPurchaseModel(
            id=str(domain.id),
            user_id=str(domain.user_id),
            pack_code=str(domain.pack_code),
            credits=domain.credits.amount,
            price_amount=domain.price.amount,
            price_currency=domain.price.currency.value,
            expires_in_days=domain.expires_in_days,
            status=domain.status.value,
            created_at=domain.created_at,
            paid_at=domain.paid_at,
            credits_granted_at=domain.credits_granted_at,
            failed_at=domain.failed_at,
            refunded_at=domain.refunded_at,
            failure_reason=domain.failure_reason,
        )

    @staticmethod
    def update_model(
        model: PaygPurchaseModel,
        domain: PaygPurchase,
    ) -> None:
        model.user_id = str(domain.user_id)
        model.credits = domain.credits.amount
        model.status = domain.status.value
        model.created_at = domain.created_at
        model.paid_at = domain.paid_at
        model.credits_granted_at = domain.credits_granted_at
        model.failed_at = domain.failed_at
        model.refunded_at = domain.refunded_at
        model.failure_reason = domain.failure_reason
