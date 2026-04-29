from abc import abstractmethod

from billing.invoice.domain.invoice import Invoice
from billing.invoice.domain.value_objects.invoice_id import InvoiceId
from billing.shared.domain.repository import Repository
from billing.shared.domain.value_objects.user_id import UserId


class InvoiceRepository(
    Repository[Invoice, InvoiceId],
):
    """Repository interface for managing Invoice entities."""

    @abstractmethod
    async def list_by_user_id(self, user_id: UserId) -> list[Invoice]:
        """List all invoices for a given user ID."""
        raise NotImplementedError

    @abstractmethod
    async def list_open_by_user_id(self, user_id: UserId) -> list[Invoice]:
        """List all open invoices for a given user ID."""
        raise NotImplementedError
