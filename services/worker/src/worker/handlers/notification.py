from dataclasses import dataclass


@dataclass(slots=True)
class NotificationHandler:
    async def handle(self, message) -> None: ...
