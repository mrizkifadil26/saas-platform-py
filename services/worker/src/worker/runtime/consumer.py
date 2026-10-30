from asyncio import Protocol


class Consumer(Protocol):
    async def run(self) -> None: ...

    async def close(self) -> None: ...
