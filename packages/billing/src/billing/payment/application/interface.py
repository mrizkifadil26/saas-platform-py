from abc import ABC, abstractmethod

from billing.payment.domain.payment_gateway import ChargeRequest, ChargeResult


class PaymentProcessor(ABC):
    @abstractmethod
    async def charge(self, request: ChargeRequest) -> ChargeResult:
        raise NotImplementedError
