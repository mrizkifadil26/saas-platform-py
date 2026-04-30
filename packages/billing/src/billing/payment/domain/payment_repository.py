from abc import abstractmethod

from billing.invoice.domain.value_objects.invoice_id import InvoiceId
from billing.payment.domain.payment import Payment
from billing.payment.domain.value_objects.payment_id import PaymentId
from billing.shared.domain.repository import Repository
from billing.shared.domain.value_objects.user_id import UserId


class PaymentRepository(
    Repository[Payment, PaymentId],
):
    """Domain-specific repository for Payment aggregate."""

    @abstractmethod
    async def find_by_invoice_id(
        self,
        invoice_id: InvoiceId,
    ) -> list[Payment]:
        """Find all payments associated with a given invoice ID."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_user_id(
        self,
        user_id: UserId,
    ) -> list[Payment]:
        """Find all payments associated with a given user ID."""
        raise NotImplementedError
