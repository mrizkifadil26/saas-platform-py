from typing import Any

from iam.shared.application.outbox import OutboxHandler


class OutboxDispatcher:
    def __init__(
        self,
        handlers: dict[
            str,
            OutboxHandler,
        ],
    ) -> None:
        self.handlers = handlers

    async def dispatch(
        self,
        message: dict[str, Any],
    ) -> None:
        handler = self.handlers.get(message["topic"])
        if handler is None:
            raise RuntimeError(f"Unknown outbox topic: {message['topic']}")

        await handler.handle(message["payload"])
