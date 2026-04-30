from billing.credits.domain.credit_source_type import CreditSourceType
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
from billing.payg.application.interfaces import PaygPricingCatalog
from billing.payg.domain.payg_purchase import PaygPurchase
from billing.payg.domain.value_objects.payg_purchase_id import PaygPurchaseId
from billing.payment.domain.payment import Payment
from billing.payment.domain.payment_gateway import ChargeRequest, PaymentGateway
from billing.payment.domain.value_objects.payment_id import PaymentId
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
        package = await self._pricing_catalog.get_payg_package(command.package_code)

        if package is None:
            raise PaygPackageNotFoundError(
                f"PAYG package not found: {command.package_code}"
            )

        now = self._clock.now()

        async with self._uow:
            purchase = PaygPurchase.create(
                purchase_id=PaygPurchaseId(self._id_generator.generate()),
                user_id=command.user_id,
                credits=package.credits,
                occurred_at=now,
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

            await self._uow.payg_purchases.save(purchase)
            await self._uow.invoices.save(invoice)
            await self._uow.payments.save(payment)
            await self._uow.commit()

            created_events = (
                purchase.pull_domain_events()
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
                    idempotency_key=command.idempotency_key,
                )
            )
        except Exception as exc:
            raise PaymentGatewayError("PAYG payment gateway charge failed.") from exc

        async with self._uow as uow:
            purchase = await uow.payg_purchases.get(purchase.id)
            invoice = await uow.invoices.get(invoice.id)
            payment = await uow.payments.get(payment.id)

            if purchase is None:
                raise PaygPurchaseNotFoundError("PAYG purchase disappeared.")

            if invoice is None:
                raise InvoiceNotFoundError("Invoice disappeared.")

            if payment is None:
                raise PaymentNotFoundError("Payment disappeared.")

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

                purchase.mark_payment_succeeded(occurred_at=occurred_at)

                credit_account = await uow.credit_accounts.get_by_user_id(
                    command.user_id
                )

                if credit_account is None:
                    raise CreditAccountNotFoundError(
                        f"Credit account not found for user: {command.user_id}"
                    )

                credit_account.grant(
                    grant_id=CreditGrantId(self._id_generator.generate()),
                    amount=purchase.credits,
                    source_type=CreditSourceType.PURCHASE,
                    source_id=str(purchase.id),
                    occurred_at=occurred_at,
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

            else:
                failure_reason = charge_result.failure_reason or "Payment failed."

                payment.mark_failed(
                    reason=failure_reason,
                    occurred_at=occurred_at,
                )

                purchase.fail(
                    reason=failure_reason,
                    occurred_at=occurred_at,
                )

                await self._uow.payments.save(payment)
                await self._uow.payg_purchases.save(purchase)
                await self._uow.commit()

                events = payment.pull_domain_events() + purchase.pull_domain_events()

        # TODO: will use await later
        self._event_publisher.publish(events)

        return PurchasePaygCreditsResultDTO(
            purchase=PaygPurchaseDTO.from_domain(purchase),
            invoice_id=str(invoice.id),
            payment_id=str(payment.id),
            amount=payment.amount.amount,
            currency=payment.amount.currency.value,
            gateway_reference=payment.gateway_reference,
        )


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

            occurred_at = self._clock.now()

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


# class PaygApplicationService:
#     def __init__(
#         self,
#         uow: PaygApplicationUnitOfWork,
#         event_publisher: EventPublisher | None = None,
#         idempotency_store: IdempotencyStore | None = None,
#     ):
#         self.uow = uow
#         self.event_publisher = event_publisher
#         self.idempotency_store = idempotency_store

#     async def create_purchase(
#         self,
#         cmd: CreatePaygPurchaseCommand,
#     ) -> PaygPurchaseResultDTO:
#         now = cmd.now or utc_now()

#         key = self._idempotency_key(str(cmd.request_id))
#         fingerprint = self._fingerprint(
#             {
#                 "user_id": str(cmd.user_id),
#                 "plan_code": str(cmd.plan_code),
#                 "request_id": str(cmd.request_id),
#                 "metadata": cmd.metadata or {},
#             }
#         )

#         await self._ensure_idempotent(key, fingerprint)

#         async with self.uow:
#             result = create_payg_purchase(
#                 purchase_id=PaygPurchaseId.new(),
#                 grant_id=GrantId.new(),
#                 user_id=cmd.user_id,
#                 plan_code=cmd.plan_code,
#                 now=now,
#                 request_id=cmd.request_id,
#                 metadata=cmd.metadata,
#             )

#             await self.uow.payg_purchase.save(
#                 result.purchase
#             )
#             await self.uow.ledger.save_grant(result.grant)
#             await self.uow.commit()

#         await self._store_idempotency(key, fingerprint)
#         await self._publish_many([result.event])

#         return to_payg_purchase_result_dto(result)

#     async def _ensure_idempotent(
#         self,
#         key: str,
#         fingerprint: str,
#     ) -> None:
#         if self.idempotency_store is None:
#             return

#         existing = await self.idempotency_store.get(key)
#         if existing is None:
#             return

#         if existing != fingerprint:
#             raise IdempotencyConflictError(
#                 f"Conflicting request for key={key}"
#             )
#         raise DuplicateRequestError(
#             f"Request for key={key} already processed"
#         )

#     async def _store_idempotency(
#         self,
#         key: str,
#         fingerprint: str,
#     ) -> None:
#         if self.idempotency_store is None:
#             return
#         await self.idempotency_store.save(key, fingerprint)

#     async def _publish_many(
#         self,
#         events: list[object],
#     ) -> None:
#         if self.event_publisher is None or not events:
#             return
#         await self.event_publisher.publish_many(events)

#     @staticmethod
#     def _idempotency_key(request_id: str) -> str:
#         return f"billing:payg:create_purchase:{request_id}"

#     @staticmethod
#     def _fingerprint(payload: dict) -> str:
#         raw = json.dumps(
#             payload,
#             sort_keys=True,
#         ).encode("utf-8")
#         return hashlib.sha256(raw).hexdigest()
