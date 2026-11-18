from dataclasses import dataclass


@dataclass(slots=True)
class EmailVerificationHandler:
    async def handle(self, message) -> None: ...
