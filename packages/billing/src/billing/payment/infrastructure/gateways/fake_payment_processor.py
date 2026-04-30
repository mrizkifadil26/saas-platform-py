from __future__ import annotations

from uuid import uuid4

from billing.payment.application.interface import PaymentProcessor
from billing.payment.domain.payment_gateway import ChargeRequest, ChargeResult


class FakePaymentProcessor(PaymentProcessor):
    def __init__(self, *, should_succeed: bool = True) -> None:
        self._should_succeed = should_succeed

    async def charge(self, request: ChargeRequest) -> ChargeResult:
        if self._should_succeed:
            return ChargeResult(
                succeeded=True,
                gateway_reference=f"fake_charge_{uuid4().hex}",
                failure_reason=None,
            )

        return ChargeResult(
            succeeded=False,
            gateway_reference=None,
            failure_reason="Fake payment failure.",
        )
