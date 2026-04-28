from __future__ import annotations

from datetime import datetime

from db.repositories import SQLAlchemyRepository

from billing.pricing.domain.pricing_rule import PricingRule
from billing.pricing.domain.pricing_rule_repository import PricingRuleRepository
from billing.pricing.domain.value_objects.pricing_key import PricingKey
from billing.pricing.infrastructure.persistence.sqlalchemy.models import (
    PricingRuleModel,
)
from billing.pricing.infrastructure.persistence.sqlalchemy.orm_mappers import (
    PricingRuleORMMapper,
)
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class SQLPricingRuleRepository(
    SQLAlchemyRepository[PricingRule, PricingKey, PricingRuleModel],
    PricingRuleRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active_by_key(
        self,
        pricing_key: PricingKey,
        *,
        at: datetime,
    ) -> PricingRule | None:
        stmt = (
            select(PricingRuleModel)
            .where(
                PricingRuleModel.pricing_key == str(pricing_key),
                PricingRuleModel.active_from <= at,
                or_(
                    PricingRuleModel.active_until.is_(None),
                    PricingRuleModel.active_until > at,
                ),
            )
            .order_by(PricingRuleModel.active_from.desc())
            .limit(1)
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return PricingRuleORMMapper.to_domain(model)

    async def save(self, pricing_rule: PricingRule) -> None:
        model = PricingRuleORMMapper.to_model(pricing_rule)

        await self._session.merge(model)
