import logging
from dataclasses import dataclass

from iam.shared.infrastructure.messaging.consumer import MessageConsumer
from iam.shared.infrastructure.messaging.message import ReceivedMessage
from iam.shared.infrastructure.messaging.registry import MessageHandlerRegistry
from iam.workers.worker import StopSignal, Worker

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class EmailVerificationWorker(Worker):
    consumer: MessageConsumer
    registry: MessageHandlerRegistry

    async def run(self, stop: StopSignal) -> None:
        logger.info("email verification worker started")

        try:
            async for received in self.consumer:
                if stop.is_stopped:
                    break

                await self._process(received)
        finally:
            logger.info("email verification worker stopped")

        # while not stop.is_stopped:
        #     await self._consumer.consume(
        #         subject="iam.email_verification.requested",
        #         consumer_name="iam.email-verification",
        #     )

        #     try:
        #         await asyncio.wait_for(
        #             stop.wait(),
        #             timeout=self._interval,
        #         )
        #     except TimeoutError:
        #         # TOOD: handle exception later
        #         pass

    async def _process(
        self,
        received: ReceivedMessage,
    ) -> None:
        message = received.message

        try:
            handler = self.registry.get(message.type)
            await handler(message)

            print(
                f"Received message: type={message.type}, id={message.id}, payload={message.payload}"
            )

        except Exception:
            logger.exception(
                "Failed to process message",
                extra={"message_id": str(message.id)},
            )

            await received.reject(requeue=True)
        else:
            await received.ack()
