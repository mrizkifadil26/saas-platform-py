from identity.shared.infrastructure.messaging.handler import MessageHandler


class MessageHandlerRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, MessageHandler] = {}

    def register(
        self,
        message_type: str,
        handler: MessageHandler,
    ) -> None:
        if message_type in self._handlers:
            raise ValueError(f"Handler already registered: {message_type}")

        self._handlers[message_type] = handler

    def get(
        self,
        message_type: str,
    ) -> MessageHandler:
        try:
            return self._handlers[message_type]
        except KeyError:
            raise LookupError(f"No handler registered for: {message_type}") from None
