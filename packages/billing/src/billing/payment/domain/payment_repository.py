from abc import abstractmethod

from billing.payment.domain.payment import Payment
from billing.payment.domain.payment_events import PaymentId
from billing.shared.domain.repository import Repository


class PaymentRepository(
    Repository[Payment, PaymentId],
):
    """Domain-specific repository for Payment aggregate."""

    @abstractmethod
    async def find_by_invoice_id(
        self,
        invoice_id: str,
    ) -> list[Payment]:
        """Find all payments associated with a given invoice ID."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_user_id(
        self,
        user_id: str,
    ) -> list[Payment]:
        """Find all payments associated with a given user ID."""
        raise NotImplementedError
