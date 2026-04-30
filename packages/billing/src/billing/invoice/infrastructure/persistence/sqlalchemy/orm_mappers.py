from billing.invoice.domain.invoice import Invoice
from billing.invoice.domain.invoice_status import InvoiceStatus
from billing.invoice.domain.value_objects.invoice_id import InvoiceId
from billing.invoice.domain.value_objects.invoice_line import InvoiceLine
from billing.invoice.infrastructure.persistence.sqlalchemy.models import (
    InvoiceLineModel,
    InvoiceModel,
)
from billing.shared.domain.value_objects.currency import Currency
from billing.shared.domain.value_objects.money import Money
from billing.shared.domain.value_objects.user_id import UserId


class InvoiceORMMapper:
    @staticmethod
    def from_model(model: InvoiceModel) -> Invoice:
        return Invoice(
            id=InvoiceId(model.id),
            user_id=UserId(model.user_id),
            status=InvoiceStatus(model.status),
            lines=[InvoiceLineORMMapper.from_model(line) for line in model.lines],
            created_at=model.created_at,
            issued_at=model.issued_at,
            paid_at=model.paid_at,
            voided_at=model.voided_at,
            uncollectible_at=model.uncollectible_at,
        )

    @staticmethod
    def to_model(domain: Invoice) -> InvoiceModel:
        return InvoiceModel(
            id=str(domain.id),
            user_id=str(domain.user_id),
            status=domain.status.value,
            created_at=domain.created_at,
            issued_at=domain.issued_at,
            paid_at=domain.paid_at,
            voided_at=domain.voided_at,
            uncollectible_at=domain.uncollectible_at,
            lines=[
                InvoiceLineORMMapper.to_model(line, position=index)
                for index, line in enumerate(domain.lines)
            ],
        )

    @staticmethod
    def update_model(
        model: InvoiceModel,
        domain: Invoice,
    ) -> None:
        model.user_id = str(domain.user_id)
        model.status = domain.status.value
        model.created_at = domain.created_at
        model.issued_at = domain.issued_at
        model.paid_at = domain.paid_at
        model.voided_at = domain.voided_at
        model.uncollectible_at = domain.uncollectible_at

        model.lines.clear()
        for index, line in enumerate(domain.lines):
            model.lines.append(InvoiceLineORMMapper.to_model(line, position=index))


class InvoiceLineORMMapper:
    @staticmethod
    def from_model(model: InvoiceLineModel) -> InvoiceLine:
        return InvoiceLine(
            description=model.description,
            quantity=model.quantity,
            unit_price=Money(model.unit_price_amount, Currency(model.currency)),
        )

    @staticmethod
    def to_model(domain: InvoiceLine, *, position: int) -> InvoiceLineModel:
        return InvoiceLineModel(
            position=position,
            description=domain.description,
            quantity=domain.quantity,
            unit_price_amount=domain.unit_price.amount,
            currency=domain.unit_price.currency.value,
        )
