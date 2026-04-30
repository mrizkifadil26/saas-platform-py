from billing.invoice.domain.value_objects.invoice_id import InvoiceId
from billing.payment.domain.payment import Payment
from billing.payment.domain.payment_status import PaymentStatus
from billing.payment.domain.value_objects.payment_id import PaymentId
from billing.payment.domain.value_objects.payment_method import (
    PaymentMethod,
    PaymentMethodType,
)
from billing.payment.infrastructure.persistence.sqlalchemy.models import PaymentModel
from billing.shared.domain.value_objects.currency import Currency
from billing.shared.domain.value_objects.money import Money
from billing.shared.domain.value_objects.user_id import UserId


class PaymentORMMapper:
    @staticmethod
    def from_model(model: PaymentModel) -> Payment:
        return Payment(
            id=PaymentId(model.id),
            user_id=UserId(model.user_id),
            invoice_id=InvoiceId(model.invoice_id),
            amount=Money(
                amount=model.amount,
                currency=Currency(model.currency),
            ),
            method=PaymentMethod(
                type=PaymentMethodType(model.method_type),
                provider=model.method_provider,
                reference=model.method_reference,
            ),
            status=PaymentStatus(model.status),
            gateway_reference=model.gateway_reference,
            failure_reason=model.failure_reason,
            created_at=model.created_at,
            processing_started_at=model.processing_started_at,
            succeeded_at=model.succeeded_at,
            failed_at=model.failed_at,
            canceled_at=model.canceled_at,
            refunded_at=model.refunded_at,
        )

    @staticmethod
    def to_model(domain: Payment) -> PaymentModel:
        return PaymentModel(
            id=str(domain.id),
            user_id=str(domain.user_id),
            invoice_id=str(domain.invoice_id),
            amount=domain.amount.amount,
            currency=domain.amount.currency.value,
            method_type=domain.method.type.value,
            method_provider=domain.method.provider,
            method_reference=domain.method.reference,
            status=domain.status.value,
            gateway_reference=domain.gateway_reference,
            failure_reason=domain.failure_reason,
            created_at=domain.created_at,
            processing_started_at=domain.processing_started_at,
            succeeded_at=domain.succeeded_at,
            failed_at=domain.failed_at,
            canceled_at=domain.canceled_at,
            refunded_at=domain.refunded_at,
        )

    @staticmethod
    def update_model(
        model: PaymentModel,
        domain: Payment,
    ) -> None:
        model.user_id = str(domain.user_id)
        model.invoice_id = str(domain.invoice_id)
        model.amount = domain.amount.amount
        model.currency = domain.amount.currency.value

        model.method_type = domain.method.type.value
        model.method_provider = domain.method.provider
        model.method_reference = domain.method.reference

        model.status = domain.status.value
        model.gateway_reference = domain.gateway_reference
        model.failure_reason = domain.failure_reason

        model.created_at = domain.created_at
        model.processing_started_at = domain.processing_started_at
        model.succeeded_at = domain.succeeded_at
        model.failed_at = domain.failed_at
        model.canceled_at = domain.canceled_at
        model.refunded_at = domain.refunded_at
