from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ConsumptionAllocationDTO:
    grant_id: str
    credits: int


@dataclass(frozen=True, slots=True)
class CreditConsumptionDTO:
    consumption_id: str
    user_id: str
    cost: int
    created_at: datetime
    allocations: tuple[ConsumptionAllocationDTO, ...]
    request_id: str | None
    metadata: dict[str, str]


def to_credit_consumption_dto(
    consumption,
) -> CreditConsumptionDTO:
    return CreditConsumptionDTO(
        consumption_id=str(consumption.consumption_id),
        user_id=str(consumption.user_id),
        cost=int(consumption.cost),
        created_at=consumption.created_at,
        allocations=tuple(
            ConsumptionAllocationDTO(
                grant_id=str(item.grant_id),
                credits=int(item.credits),
            )
            for item in consumption.allocations
        ),
        request_id=str(consumption.request_id)
        if consumption.request_id is not None
        else None,
        metadata=dict(consumption.metadata),
    )
