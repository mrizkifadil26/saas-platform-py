from asyncio import Protocol


class EmailTemplate(Protocol):
    name: str
    recipient: str

    def context(self) -> dict[str, object]: ...
