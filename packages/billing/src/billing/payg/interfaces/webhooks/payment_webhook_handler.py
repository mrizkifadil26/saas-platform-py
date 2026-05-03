from __future__ import annotations

from billing.payg.application.commands import GrantPaygCreditsCommand
from billing.payg.application.handlers import GrantPaygCreditsHandler
from billing.payg.domain.value_objects.payg_purchase_id import PaygPurchaseId
from billing.payg.interfaces.webhooks.schemas import PaymentSucceededEvent


class PaymentWebhookHandler:
    def __init__(
        self,
        *,
        grant_handler: GrantPaygCreditsHandler,
    ) -> None:
        self._grant_handler = grant_handler

    async def handle_payment_succeeded(
        self,
        event: PaymentSucceededEvent,
    ) -> None:
        command = GrantPaygCreditsCommand(
            purchase_id=PaygPurchaseId(event.purchase_id),
        )

        await self._grant_handler.handle(command)
