from abc import ABC
from typing import Iterable


class EventPublisher(ABC):
    def publish(
        self,
        events: Iterable[object],
    ) -> None:
        raise NotImplementedError
