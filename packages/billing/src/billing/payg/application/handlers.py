from billing.credits.domain.credit_account import CreditAccount
from billing.credits.domain.credit_source_type import CreditSourceType
from billing.credits.domain.value_objects.credit_account_id import CreditAccountId
from billing.credits.domain.value_objects.credit_grant_id import CreditGrantId
from billing.invoice.domain.invoice import Invoice
from billing.invoice.domain.value_objects.invoice_id import InvoiceId
from billing.invoice.domain.value_objects.invoice_line import InvoiceLine
from billing.payg.application.commands import (
    GrantPaygCreditsCommand,
    MarkPaygPaymentFailedCommand,
    MarkPaygPaymentSucceededCommand,
    PurchasePaygCreditsCommand,
)
from billing.payg.application.dto import PaygPurchaseDTO, PurchasePaygCreditsResultDTO
from billing.payg.application.exceptions import (
    CreditAccountNotFoundError,
    InvoiceNotFoundError,
    PaygPackageNotFoundError,
    PaygPurchaseNotFoundError,
    PaymentGatewayError,
    PaymentNotFoundError,
)
from billing.payg.config import PAYG_EXPIRY_DAYS
from billing.payg.domain.payg_purchase import PaygPurchase
from billing.payg.domain.value_objects.payg_purchase_id import PaygPurchaseId
from billing.payment.domain.payment import Payment
from billing.payment.domain.payment_gateway import ChargeRequest, PaymentGateway
from billing.payment.domain.value_objects.payment_id import PaymentId
from billing.pricing.application.catalogs import PaygPricingCatalog
from billing.shared.application.clock import Clock
from billing.shared.application.event_publisher import EventPublisher
from billing.shared.application.id_generator import IdGenerator
from billing.shared.application.uow import BillingUoW


class PurchasePaygCreditsHandler:
    """
    Main PAYG checkout use case.

    Flow:
    1. Load package from pricing
    2. Create PAYG purchase
    3. Create invoice
    4. Create payment
    5. Commit local state
    6. Charge gateway outside DB transaction
    7. Reload everything
    8. If succeeded:
       - mark payment succeeded
       - mark invoice paid
       - mark payg payment succeeded
       - grant credits
       - mark payg credits granted
    9. If failed:
       - mark payment failed
       - mark payg failed
    """

    def __init__(
        self,
        *,
        uow: BillingUoW,
        pricing_catalog: PaygPricingCatalog,
        payment_gateway: PaymentGateway,
        clock: Clock,
        id_generator: IdGenerator,
        event_publisher: EventPublisher,
    ) -> None:
        self._uow = uow
        self._pricing_catalog = pricing_catalog
        self._payment_gateway = payment_gateway
        self._clock = clock
        self._id_generator = id_generator
        self._event_publisher = event_publisher

    async def handle(
        self,
        command: PurchasePaygCreditsCommand,
    ) -> PurchasePaygCreditsResultDTO:
        package = await self._pricing_catalog.get_payg_package(command.pack_code)

        if package is None:
            raise PaygPackageNotFoundError(
                f"PAYG package not found: {command.pack_code}"
            )

        now = self._clock.now()

        async with self._uow as uow:
            credit_account = await uow.credit_accounts.get_by_user_id(command.user_id)
            if credit_account is None:
                credit_account = CreditAccount.create(
                    id=CreditAccountId(self._id_generator.generate()),
                    user_id=command.user_id,
                )
                await uow.credit_accounts.save(credit_account)

            purchase = PaygPurchase.create(
                purchase_id=PaygPurchaseId(self._id_generator.generate()),
                user_id=command.user_id,
                credits=package.credits,
                occurred_at=now,
                pack_code=package.code,
                price=package.price,
                expires_in_days=PAYG_EXPIRY_DAYS,
            )

            invoice = Invoice.create(
                invoice_id=InvoiceId(self._id_generator.generate()),
                user_id=command.user_id,
                lines=[
                    InvoiceLine(
                        description=f"PAYG credits package: {package.name}",
                        quantity=1,
                        unit_price=package.price,
                    )
                ],
                occurred_at=now,
            )
            invoice.issue(occurred_at=now)

            payment = Payment.create(
                id=PaymentId(self._id_generator.generate()),
                user_id=command.user_id,
                invoice_id=invoice.id,
                amount=invoice.total,
                method=command.payment_method,
                created_at=now,
            )
            payment.start_processing(occurred_at=now)

            await uow.payg_purchases.save(purchase)
            await uow.invoices.save(invoice)
            await uow.payments.save(payment)
            await uow.commit()

            created_events = (
                credit_account.pull_domain_events()
                + purchase.pull_domain_events()
                + invoice.pull_domain_events()
                + payment.pull_domain_events()
            )

        # TODO: will use await later
        self._event_publisher.publish(created_events)

        try:
            charge_result = await self._payment_gateway.charge(
                ChargeRequest(
                    payment_id=payment.id,
                    user_id=command.user_id,
                    invoice_id=invoice.id,
                    amount=invoice.total,
                    method=command.payment_method,
                    # idempotency_key=command.idempotency_key,
                    idempotency_key="dummy",  # TODO: implement idempotency later
                )
            )
        except Exception as exc:
            payment = await self._mark_gateway_exception(
                payment_id=payment.id,
                purchase_id=purchase.id,
                reason="PAYG payment gateway charge raised an exception.",
            )

            raise PaymentGatewayError("PAYG payment gateway charge failed.") from exc

        if charge_result.succeeded:
            if charge_result.gateway_reference is None:
                await self._mark_gateway_exception(
                    payment_id=payment.id,
                    purchase_id=purchase.id,
                    reason="Gateway returned success without gateway reference.",
                )
                raise PaymentGatewayError(
                    "Gateway returned success without gateway reference."
                )

            purchase, invoice, payment = await self._apply_successful_charge(
                purchase_id=purchase.id,
                invoice_id=invoice.id,
                payment_id=payment.id,
                gateway_reference=charge_result.gateway_reference,
            )
        else:
            failure_reason = charge_result.failure_reason or "Payment failed."

            purchase, invoice, payment = await self._apply_failed_charge(
                purchase_id=purchase.id,
                invoice_id=invoice.id,
                payment_id=payment.id,
                reason=failure_reason,
            )

        return PurchasePaygCreditsResultDTO(
            purchase=PaygPurchaseDTO.from_domain(purchase),
            invoice_id=str(invoice.id),
            payment_id=str(payment.id),
            amount=payment.amount.amount,
            currency=payment.amount.currency.value,
            gateway_reference=payment.gateway_reference,
        )

    async def _apply_successful_charge(
        self,
        *,
        purchase_id: PaygPurchaseId,
        invoice_id: InvoiceId,
        payment_id: PaymentId,
        gateway_reference: str,
    ) -> tuple[PaygPurchase, Invoice, Payment]:
        occurred_at = self._clock.now()

        async with self._uow as uow:
            purchase = await uow.payg_purchases.get(purchase_id)
            invoice = await uow.invoices.get(invoice_id)
            payment = await uow.payments.get(payment_id)

            if purchase is None:
                raise PaygPurchaseNotFoundError("PAYG purchase disappeared.")

            if invoice is None:
                raise InvoiceNotFoundError("Invoice disappeared.")

            if payment is None:
                raise PaymentNotFoundError("Payment disappeared.")

            credit_account = await uow.credit_accounts.get_by_user_id(purchase.user_id)

            if credit_account is None:
                credit_account = CreditAccount.create(
                    id=CreditAccountId(self._id_generator.generate()),
                    user_id=purchase.user_id,
                )

            payment.mark_succeeded(
                gateway_reference=gateway_reference,
                occurred_at=occurred_at,
            )

            invoice.mark_paid(occurred_at=occurred_at)

            purchase.mark_payment_succeeded(occurred_at=occurred_at)

            credit_account.grant(
                grant_id=CreditGrantId(self._id_generator.generate()),
                amount=purchase.credits,
                source_type=CreditSourceType.PURCHASE,
                source_id=str(purchase.id),
                occurred_at=occurred_at,
                description=f"PAYG purchase {purchase.id}",
            )

            purchase.mark_credits_granted(occurred_at=occurred_at)

                await self._uow.payments.save(payment)
                await self._uow.invoices.save(invoice)
                await self._uow.credit_accounts.save(credit_account)
                await self._uow.payg_purchases.save(purchase)
                await self._uow.commit()

            events = (
                payment.pull_domain_events()
                + invoice.pull_domain_events()
                + credit_account.pull_domain_events()
                + purchase.pull_domain_events()
            )

        self._event_publisher.publish(events)

        return purchase, invoice, payment

    async def _apply_failed_charge(
        self,
        *,
        purchase_id: PaygPurchaseId,
        invoice_id: InvoiceId,
        payment_id: PaymentId,
        reason: str,
    ) -> tuple[PaygPurchase, Invoice, Payment]:
        occurred_at = self._clock.now()

        async with self._uow as uow:
            purchase = await uow.payg_purchases.get(purchase_id)
            invoice = await uow.invoices.get(invoice_id)
            payment = await uow.payments.get(payment_id)

            if purchase is None:
                raise PaygPurchaseNotFoundError("PAYG purchase disappeared.")

            if invoice is None:
                raise InvoiceNotFoundError("Invoice disappeared.")

            if payment is None:
                raise PaymentNotFoundError("Payment disappeared.")

            payment.mark_failed(
                reason=reason,
                occurred_at=occurred_at,
            )

            purchase.fail(
                reason=reason,
                occurred_at=occurred_at,
            )

            await uow.payments.save(payment)
            await uow.payg_purchases.save(purchase)
            await uow.commit()

        events = payment.pull_domain_events() + purchase.pull_domain_events()
        self._event_publisher.publish(events)

        return purchase, invoice, payment

    async def _mark_gateway_exception(
        self,
        *,
        payment_id: PaymentId,
        purchase_id: PaygPurchaseId,
        reason: str,
    ) -> Payment | None:
        occurred_at = self._clock.now()

        async with self._uow as uow:
            payment = await uow.payments.get(payment_id)
            purchase = await uow.payg_purchases.get(purchase_id)

            if payment is None:
                return None

            payment.mark_failed(
                reason=reason,
                occurred_at=occurred_at,
            )

            if purchase is not None:
                purchase.fail(
                    reason=reason,
                    occurred_at=occurred_at,
                )

            await uow.payments.save(payment)

            if purchase is not None:
                await uow.payg_purchases.save(purchase)

            await uow.commit()

        events = payment.pull_domain_events()

        if purchase is not None:
            events += purchase.pull_domain_events()

        self._event_publisher.publish(events)

        return payment


class MarkPaygPaymentSucceededHandler:
    """
    Use this for async webhook flow if the gateway does not return final success
    immediately.

    It assumes payment already exists.
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

    async def handle(
        self,
        command: MarkPaygPaymentSucceededCommand,
    ) -> PaygPurchaseDTO:
        async with self._uow:
            purchase = await self._uow.payg_purchases.get(command.purchase_id)

            if purchase is None:
                raise PaygPurchaseNotFoundError(
                    f"PAYG purchase not found: {command.purchase_id}"
                )

            purchase.mark_payment_succeeded(occurred_at=self._clock.now())

            await self._uow.payg_purchases.save(purchase)
            await self._uow.commit()

            events = purchase.pull_domain_events()

        # TODO: will use await later
        self._event_publisher.publish(events)

        return PaygPurchaseDTO.from_domain(purchase)


class MarkPaygPaymentFailedHandler:
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

    async def handle(
        self,
        command: MarkPaygPaymentFailedCommand,
    ) -> PaygPurchaseDTO:
        async with self._uow:
            purchase = await self._uow.payg_purchases.get(command.purchase_id)

            if purchase is None:
                raise PaygPurchaseNotFoundError(
                    f"PAYG purchase not found: {command.purchase_id}"
                )

            purchase.fail(
                reason=command.reason,
                occurred_at=self._clock.now(),
            )

            await self._uow.payg_purchases.save(purchase)
            await self._uow.commit()

            events = purchase.pull_domain_events()

        # TODO: will use await later
        self._event_publisher.publish(events)

        return PaygPurchaseDTO.from_domain(purchase)


class GrantPaygCreditsHandler:
    """
    Use this if credit granting is async/event-driven.

    In the synchronous PurchasePaygCreditsHandler above, credits are granted inline.
    For production, you may later split this into an event handler reacting to
    PaymentSucceeded/InvoicePaid.
    """

    def __init__(
        self,
        *,
        uow: BillingUoW,
        clock: Clock,
        id_generator: IdGenerator,
        event_publisher: EventPublisher,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._id_generator = id_generator
        self._event_publisher = event_publisher

    async def handle(self, command: GrantPaygCreditsCommand) -> PaygPurchaseDTO:
        async with self._uow:
            purchase = await self._uow.payg_purchases.get(command.purchase_id)

            if purchase is None:
                raise PaygPurchaseNotFoundError(
                    f"PAYG purchase not found: {command.purchase_id}"
                )

            credit_account = await self._uow.credit_accounts.get_by_user_id(
                purchase.user_id
            )

            if credit_account is None:
                raise CreditAccountNotFoundError(
                    f"Credit account not found for user: {purchase.user_id}"
                )

            credit_account.grant(
                grant_id=CreditGrantId(self._id_generator.generate()),
                amount=purchase.credits,
                source_type=CreditSourceType.PURCHASE,
                source_id=str(purchase.id),
                occurred_at=occurred_at,
            )

            purchase.mark_credits_granted(occurred_at=occurred_at)

            await self._uow.credit_accounts.save(credit_account)
            await self._uow.payg_purchases.save(purchase)
            await self._uow.commit()

            events = credit_account.pull_domain_events() + purchase.pull_domain_events()

        # TODO: will use await later
        self._event_publisher.publish(events)

        return PaygPurchaseDTO.from_domain(purchase)
