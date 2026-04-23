from db.repositories import SQLAlchemyRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from billing.shared.domain.value_objects.user_id import UserId
from billing.subscription.domain.subscription import Subscription
from billing.subscription.domain.subscription_repository import SubscriptionRepository
from billing.subscription.domain.subscription_status import SubscriptionStatus
from billing.subscription.domain.value_objects.subscription_id import SubscriptionId
from billing.subscription.infrastructure.persistence.sqlalchemy.mappers.subscription_orm_mapper import (
    SubscriptionORMMapper,
)
from billing.subscription.infrastructure.persistence.sqlalchemy.models.subscription_model import (
    SubscriptionModel,
)


class SQLSubscriptionRepository(
    SQLAlchemyRepository[Subscription, str, SubscriptionModel],
    SubscriptionRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    @property
    def model_type(self) -> type[SubscriptionModel]:
        return SubscriptionModel

    def _to_domain(self, model: SubscriptionModel) -> Subscription:
        return SubscriptionORMMapper.to_domain(model)

    def _to_model(self, entity: Subscription) -> SubscriptionModel:
        return SubscriptionORMMapper.to_model(entity)

    # async def get(
    #     self,
    #     subscription_id: str,
    # ) -> Subscription | None:
    #     model = self._session.get(
    #         SubscriptionModel,
    #         # str(subscription_id),
    #         subscription_id,
    #     )
    #     if model is None:
    #         return None

    #     return SubscriptionORMMapper.to_domain(model)

    async def save(self, entity: Subscription) -> None:
        existing = await self._session.get(
            SubscriptionModel,
            str(entity.subscription_id),
        )

        if existing is None:
            model = self._to_model(entity)
            self._session.add(model)
            return

        SubscriptionORMMapper.update_model(existing, entity)

    async def delete(self, entity: Subscription) -> None:
        existing = self._session.get(
            SubscriptionModel,
            str(entity.subscription_id),
        )
        if existing is not None:
            await self._session.delete(existing)

    async def find_active_by_user(
        self,
        user_id: UserId,
    ) -> Subscription | None:
        stmt = (
            select(SubscriptionModel)
            .where(
                SubscriptionModel.user_id == str(user_id),
                SubscriptionModel.status.in_(
                    [
                        SubscriptionStatus.ACTIVE.value,
                        SubscriptionStatus.TRIALING.value,
                        SubscriptionStatus.PAST_DUE.value,
                    ]
                ),
            )
            .order_by(SubscriptionModel.current_period_end.desc())
            .limit(1)
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None

        return self._to_domain(model)

    async def find_due_for_renewal(self) -> list[Subscription]:
        stmt = select(SubscriptionModel).where(
            SubscriptionModel.status.in_(
                [
                    SubscriptionStatus.ACTIVE.value,
                    SubscriptionStatus.PAST_DUE.value,
                ]
            ),
            SubscriptionModel.cancel_at_period_end.is_(False),
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def find_canceling_subscriptions(self) -> list[Subscription]:
        stmt = select(SubscriptionModel).where(
            SubscriptionModel.cancel_at_period_end.is_(True),
            SubscriptionModel.status.in_(
                [
                    SubscriptionStatus.ACTIVE.value,
                    SubscriptionStatus.PAST_DUE.value,
                    SubscriptionStatus.TRIALING.value,
                    SubscriptionStatus.PAUSED.value,
                ]
            ),
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]
