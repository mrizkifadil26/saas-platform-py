class EventSerializationError(Exception):
    """Raised when an event cannot be serialized or deserialized."""


class UnknownEventTypeError(EventSerializationError):
    def __init__(self, event_type: str) -> None:
        super().__init__(f"Unknown event type: {event_type!r}")


class EventTypeAlreadyRegisteredError(EventSerializationError):
    def __init__(self, event_type: str) -> None:
        super().__init__(f"Event type is already registered: {event_type!r}")


class InvalidEventPayloadError(EventSerializationError):
    pass
