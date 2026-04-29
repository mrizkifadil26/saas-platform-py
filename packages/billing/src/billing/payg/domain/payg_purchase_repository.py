from billing.payg.domain.payg_purchase import PaygPurchase
from billing.payg.domain.value_objects.payg_purchase_id import PaygPurchaseId
from billing.shared.domain.repository import Repository


class PaygPurchaseRepository(
    Repository[PaygPurchase, PaygPurchaseId],
):
    """
    Domain-specific repository for PaygPurchase aggregate.

    Extends the generic Repository and adds
    query methods that are meaningful for the domain.
    """

    pass
