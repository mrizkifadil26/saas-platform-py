from dataclasses import dataclass, field
from typing import Any, Dict, Protocol, runtime_checkable


class StopPipeline(Exception):
    """Short-circuit the pipeline and return result immediately."""

    def __init__(self, result: dict):
        self.result = result
        super().__init__("Pipeline stopped")


@dataclass
class PipelineContext:
    key: str
    input: Dict[str, Any] = field(default_factory=dict)
    data: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)

    def set_source(self, source: str) -> None:
        self.meta["source"] = source


@runtime_checkable
class PipelineStage(Protocol):
    name: str

    async def run(self, ctx: PipelineContext) -> None: ...


class Pipeline:
    def __init__(self, stages: list[PipelineStage]) -> None:
        self.stages = stages

    async def run(self, ctx: PipelineContext) -> Dict[str, Any]:
        try:
            for stage in self.stages:
                await stage.run(ctx)
            return ctx.data
        except StopPipeline as e:
            return e.result