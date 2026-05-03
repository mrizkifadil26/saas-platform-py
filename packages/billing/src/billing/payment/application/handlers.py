from __future__ import annotations

from billing.payment.application.commands import (
    CancelPaymentCommand,
    ChargeInvoiceCommand,
    MarkPaymentFailedCommand,
    MarkPaymentSucceededCommand,
    RefundPaymentCommand,
)
from billing.payment.application.dto import PaymentDTO
from billing.payment.application.exceptions import (
    InvoiceNotFoundError,
    InvoiceNotPayableError,
    PaymentGatewayError,
    PaymentNotFoundError,
)
from billing.payment.domain.payment import Payment
from billing.payment.domain.payment_gateway import ChargeRequest, PaymentGateway
from billing.payment.domain.value_objects.payment_id import PaymentId
from billing.shared.application.clock import Clock
from billing.shared.application.event_publisher import EventPublisher
from billing.shared.application.id_generator import IdGenerator
from billing.shared.application.uow import BillingUoW


class ChargeInvoiceHandler:
    """
    Main payment use case.

    Flow:
    1. Load invoice
    2. Validate invoice is payable
    3. Create payment
    4. Mark payment processing
    5. Persist invoice/payment
    6. Call gateway outside transaction
    7. Reload payment/invoice
    8. Mark success/failure
    9. Mark invoice paid on success
    """

    def __init__(
        self,
        *,
        uow: BillingUoW,
        clock: Clock,
        id_generator: IdGenerator,
        payment_gateway: PaymentGateway,
        event_publisher: EventPublisher,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._id_generator = id_generator
        self._payment_gateway = payment_gateway
        self._event_publisher = event_publisher

    async def handle(self, command: ChargeInvoiceCommand) -> PaymentDTO:
        now = self._clock.now()

        async with self._uow as uow:
            invoice = await uow.invoices.get(command.invoice_id)

            if invoice is None:
                raise InvoiceNotFoundError(f"Invoice not found: {command.invoice_id}")

            if not invoice.is_payable:
                raise InvoiceNotPayableError(
                    f"Invoice is not payable from state: {invoice.status}"
                )

            payment = Payment.create(
                id=PaymentId(self._id_generator.generate()),
                user_id=invoice.user_id,
                invoice_id=invoice.id,
                amount=invoice.total,
                method=command.payment_method,
                created_at=now,
            )

            payment.start_processing(occurred_at=now)

            await uow.payments.save(payment)
            await uow.commit()

        created_events = payment.pull_domain_events()
        # TODO: later we should use await
        self._event_publisher.publish(created_events)

        try:
            charge_result = await self._payment_gateway.charge(
                ChargeRequest(
                    payment_id=payment.id,
                    user_id=payment.user_id,
                    invoice_id=payment.invoice_id,
                    amount=payment.amount,
                    method=payment.method,
                    idempotency_key=command.idempotency_key,
                )
            )
        except Exception as exc:
            raise PaymentGatewayError("Payment gateway charge failed.") from exc

        async with self._uow as uow:
            invoice = await uow.invoices.get(command.invoice_id)
            payment = await uow.payments.get(payment.id)

            if invoice is None:
                raise InvoiceNotFoundError(f"Invoice not found: {command.invoice_id}")

            if payment is None:
                raise PaymentNotFoundError("Payment disappeared after gateway charge.")

            occurred_at = self._clock.now()

            if charge_result.succeeded:
                if charge_result.gateway_reference is None:
                    raise PaymentGatewayError(
                        "Gateway returned success without gateway reference."
                    )

                payment.mark_succeeded(
                    gateway_reference=charge_result.gateway_reference,
                    occurred_at=occurred_at,
                )

                invoice.mark_paid(occurred_at=occurred_at)

                await uow.payments.save(payment)
                await uow.invoices.save(invoice)
                await uow.commit()

                events = payment.pull_domain_events() + invoice.pull_domain_events()

            else:
                payment.mark_failed(
                    reason=charge_result.failure_reason or "Payment failed.",
                    occurred_at=occurred_at,
                )

                await uow.payments.save(payment)
                await uow.commit()

                events = payment.pull_domain_events()

        # TODO: later we should use await
        self._event_publisher.publish(events)

        return PaymentDTO.from_domain(payment)


class MarkPaymentSucceededHandler:
    """
    Use this for webhooks/admin/manual reconciliation.

    It marks payment succeeded and marks the linked invoice paid.
    """

    def __init__(
        self,
        *,
        uow: BillingUoW,
        clock: Clock,
        event_publisher: EventPublisher,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._event_publisher = event_publisher

    async def handle(self, command: MarkPaymentSucceededCommand) -> PaymentDTO:
        async with self._uow as uow:
            payment = await uow.payments.get(command.payment_id)

            if payment is None:
                raise PaymentNotFoundError(f"Payment not found: {command.payment_id}")

            invoice = await uow.invoices.get(payment.invoice_id)

            if invoice is None:
                raise InvoiceNotFoundError(f"Invoice not found: {payment.invoice_id}")

            occurred_at = self._clock.now()

            payment.mark_succeeded(
                gateway_reference=command.gateway_reference,
                occurred_at=occurred_at,
            )

            if invoice.is_payable:
                invoice.mark_paid(occurred_at=occurred_at)

            await uow.payments.save(payment)
            await uow.invoices.save(invoice)
            await uow.commit()

        events = payment.pull_domain_events() + invoice.pull_domain_events()
        # TODO: later we should use await
        self._event_publisher.publish(events)

        return PaymentDTO.from_domain(payment)


class MarkPaymentFailedHandler:
    """
    Use this for webhooks/admin/manual failure events.
    """

    def __init__(
        self,
        *,
        uow: BillingUoW,
        clock: Clock,
        event_publisher: EventPublisher,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._event_publisher = event_publisher

    async def handle(self, command: MarkPaymentFailedCommand) -> PaymentDTO:
        async with self._uow as uow:
            payment = await uow.payments.get(command.payment_id)

            if payment is None:
                raise PaymentNotFoundError(f"Payment not found: {command.payment_id}")

            payment.mark_failed(
                reason=command.reason,
                occurred_at=self._clock.now(),
            )

            await uow.payments.save(payment)
            await uow.commit()

        events = payment.pull_domain_events()
        # TODO: later we should use await
        self._event_publisher.publish(events)

        return PaymentDTO.from_domain(payment)


class CancelPaymentHandler:
    def __init__(
        self,
        *,
        uow: BillingUoW,
        clock: Clock,
        event_publisher: EventPublisher,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._event_publisher = event_publisher

    async def handle(self, command: CancelPaymentCommand) -> PaymentDTO:
        async with self._uow as uow:
            payment = await uow.payments.get(command.payment_id)

            if payment is None:
                raise PaymentNotFoundError(f"Payment not found: {command.payment_id}")

            payment.cancel(occurred_at=self._clock.now())

            await uow.payments.save(payment)
            await uow.commit()

        events = payment.pull_domain_events()
        # TODO: later we should use await
        self._event_publisher.publish(events)

        return PaymentDTO.from_domain(payment)


class RefundPaymentHandler:
    """
    Minimal domain-side refund.

    Later, production version should call gateway.refund() first/around this,
    same pattern as ChargeInvoiceHandler.
    """

    def __init__(
        self,
        *,
        uow: BillingUoW,
        clock: Clock,
        event_publisher: EventPublisher,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._event_publisher = event_publisher

    async def handle(self, command: RefundPaymentCommand) -> PaymentDTO:
        async with self._uow as uow:
            payment = await uow.payments.get(command.payment_id)

            if payment is None:
                raise PaymentNotFoundError(f"Payment not found: {command.payment_id}")

            payment.refund(occurred_at=self._clock.now())

            await uow.payments.save(payment)
            await uow.commit()

        events = payment.pull_domain_events()
        # TODO: later we should use await
        self._event_publisher.publish(events)

        return PaymentDTO.from_domain(payment)
