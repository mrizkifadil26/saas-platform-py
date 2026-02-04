
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(frozen=True)
class StageSpec:
    stage: str
    enabled: bool = True
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PipelineConfig:
    name: str
    stages: list[StageSpec] = field(default_factory=list)
