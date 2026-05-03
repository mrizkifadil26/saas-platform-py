from __future__ import annotations

from billing.invoice.application.commands import (
    CreateInvoiceCommand,
    IssueInvoiceCommand,
    MarkInvoicePaidCommand,
    MarkInvoiceUncollectibleCommand,
    VoidInvoiceCommand,
)
from billing.invoice.application.dto import InvoiceDTO
from billing.invoice.application.exceptions import InvoiceNotFoundError
from billing.invoice.domain.invoice import Invoice
from billing.invoice.domain.value_objects.invoice_id import InvoiceId
from billing.invoice.domain.value_objects.invoice_line import InvoiceLine
from billing.shared.application.clock import Clock
from billing.shared.application.event_publisher import EventPublisher
from billing.shared.application.id_generator import IdGenerator
from billing.shared.application.uow import BillingUoW


class CreateInvoiceHandler:
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

    async def handle(self, command: CreateInvoiceCommand) -> InvoiceDTO:
        now = self._clock.now()

        invoice = Invoice.create(
            invoice_id=InvoiceId(self._id_generator.generate()),
            user_id=command.user_id,
            lines=[
                InvoiceLine(
                    description=line.description,
                    quantity=line.quantity,
                    unit_price=line.unit_price,
                )
                for line in command.lines
            ],
            occurred_at=now,
        )

        if command.auto_issue:
            invoice.issue(occurred_at=now)

        async with self._uow as uow:
            await uow.invoices.save(invoice)
            await uow.commit()

        events = invoice.pull_domain_events()
        # TODO: should use await cause we want to guarantee the events are published before returning the response?
        self._event_publisher.publish(events)

        return InvoiceDTO.from_domain(invoice)


class IssueInvoiceHandler:
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

    async def handle(self, command: IssueInvoiceCommand) -> InvoiceDTO:
        async with self._uow as uow:
            invoice = await uow.invoices.get(command.invoice_id)

            if invoice is None:
                raise InvoiceNotFoundError(f"Invoice not found: {command.invoice_id}")

            invoice.issue(occurred_at=self._clock.now())

            await uow.invoices.save(invoice)
            await uow.commit()

        events = invoice.pull_domain_events()
        # TODO: should use await cause we want to guarantee the events are published before returning the response?
        self._event_publisher.publish(events)

        return InvoiceDTO.from_domain(invoice)


class MarkInvoicePaidHandler:
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

    async def handle(self, command: MarkInvoicePaidCommand) -> InvoiceDTO:
        async with self._uow as uow:
            invoice = await uow.invoices.get(command.invoice_id)

            if invoice is None:
                raise InvoiceNotFoundError(f"Invoice not found: {command.invoice_id}")

            invoice.mark_paid(occurred_at=self._clock.now())

            await uow.invoices.save(invoice)
            await uow.commit()

        events = invoice.pull_domain_events()
        # TODO: should use await cause we want to guarantee the events are published before returning the response?
        self._event_publisher.publish(events)

        return InvoiceDTO.from_domain(invoice)


class VoidInvoiceHandler:
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

    async def handle(self, command: VoidInvoiceCommand) -> InvoiceDTO:
        async with self._uow as uow:
            invoice = await uow.invoices.get(command.invoice_id)

            if invoice is None:
                raise InvoiceNotFoundError(f"Invoice not found: {command.invoice_id}")

            invoice.void(occurred_at=self._clock.now())

            await uow.invoices.save(invoice)
            await uow.commit()

        events = invoice.pull_domain_events()
        # TODO: should use await cause we want to guarantee the events are published before returning the response?
        self._event_publisher.publish(events)

        return InvoiceDTO.from_domain(invoice)


class MarkInvoiceUncollectibleHandler:
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

    async def handle(self, command: MarkInvoiceUncollectibleCommand) -> InvoiceDTO:
        async with self._uow as uow:
            invoice = await uow.invoices.get(command.invoice_id)

            if invoice is None:
                raise InvoiceNotFoundError(f"Invoice not found: {command.invoice_id}")

            invoice.mark_uncollectible(occurred_at=self._clock.now())

            await uow.invoices.save(invoice)
            await uow.commit()

        events = invoice.pull_domain_events()
        # TODO: should use await cause we want to guarantee the events are published before returning the response?
        self._event_publisher.publish(events)

        return InvoiceDTO.from_domain(invoice)
