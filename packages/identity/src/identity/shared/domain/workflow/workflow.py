from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Generic, Protocol, TypeVar

T = TypeVar("T")


class WorkflowState(StrEnum):
    """Base type for workflow states."""

    pass


@dataclass(slots=True)
class StepResult:
    next_state: type[WorkflowState] | None = None
    data: dict[str, object] = field(default_factory=lambda: dict())


class WorkflowStep(Protocol, Generic[T]):
    async def execute(
        self,
        subject: T,
    ) -> StepResult: ...


@dataclass(frozen=True, slots=True)
class Transition(Generic[T]):
    source: WorkflowState
    target: WorkflowState
    step: WorkflowStep[T]


class Workflow(Generic[T], ABC):
    @property
    @abstractmethod
    def initial_state(self) -> WorkflowState:
        raise NotImplementedError

    @abstractmethod
    def can_transition(
        self,
        subject: T,
        target: WorkflowState,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def transition(
        self,
        subject: T,
        target: WorkflowState,
    ) -> None:
        raise NotImplementedError
