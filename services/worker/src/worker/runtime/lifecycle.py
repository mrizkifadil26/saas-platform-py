
import asyncio
import signal
from collections.abc import Awaitable, Callable
from types import FrameType

ShutdownCallback = Callable[[], Awaitable[None]]


class Lifecycle:
    def __init__(self) -> None:
        self._stop = asyncio.Event()
        self._shutdown_callbacks: list[ShutdownCallback] = []
        self._stopped: bool = False

    @property
    def stopped(self) -> bool:
        return self._stop.is_set()

    def add_shutdown_callback(
        self,
        callback: ShutdownCallback,
    ) -> None:
        self._shutdown_callbacks.append(callback)

    def install_signal_handlers(self) -> None:
        loop = asyncio.get_running_loop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(
                    sig,
                    self.stop,
                )
            except NotImplementedError:
                signal.signal(sig, self._handle_signal)

    def _handle_signal(
        self,
        signum: int,
        frame: FrameType | None,
    ):
        self.stop()

    def stop(self) -> None:
        self._stop.set()

    async def wait(self) -> None:
        await self._stop.wait()

    async def shutdown(self) -> None:
        if self._stopped:
            return

        self._stopped = True

        for callback in reversed(self._shutdown_callbacks):
            await callback()
