from dataclasses import dataclass
from typing import Literal


PlanKind = Literal["subscription", "payg"]


@dataclass(frozen=True)
class Plan:
    code: PlanCode
    kind: PlanKind
    tier: str
    billing_interval: Optional[str]
    credits_grant: Credits
    