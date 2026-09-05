from typing import Any, Protocol


class EmailSender(Protocol):
    async def send(
        self,
        *,
        to: str,
        template: str,
        variables: dict[str, Any],
    ) -> None: ...
