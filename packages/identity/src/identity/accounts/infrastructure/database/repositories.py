from identity.identity.application.ports import EmailVerificationRepository, UserRepository
from identity.identity.domain import (
    EmailVerification,
    User,
)
from identity.identity.domain.value_objects import (
    Email,
    EmailVerificationId,
    EmailVerificationTokenHash,
    UserId,
)
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import EmailVerificationModel, UserModel
from .orm_mappers import EmailVerificationORMMapper, UserORMMapper


class SQLAlchemyUserRepository(
    UserRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user: User) -> None:
        model = self._to_model(user)
        self._session.add(model)

    async def update(self, user: User) -> None:
        model = await self._session.get(UserModel, user.id.value)
        if model is None:
            # raise not found error
            raise RuntimeError

        UserORMMapper.update_model(model, user)

    async def find_by_id(self, user_id: UserId) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id.value)

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def find_by_email(self, email: Email) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email.value)

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def list(self, *, limit: int, offset: int) -> tuple[list[User], int]:
        users_stmt = (
            select(UserModel).order_by(UserModel.created_at.desc()).limit(limit).offset(offset)
        )

        total_stmt = select(func.count()).select_from(UserModel)

        users_result = await self._session.execute(users_stmt)
        total_result = await self._session.execute(total_stmt)

        models = users_result.scalars().all()
        total = total_result.scalar_one()

        return [self._to_domain(model) for model in models], total

    @property
    def model_type(self) -> type[UserModel]:
        return UserModel

    def _to_domain(self, model: UserModel) -> User:
        return UserORMMapper.to_domain(model)

    def _to_model(self, entity: User) -> UserModel:
        return UserORMMapper.to_model(entity)


class SQLAlchemyEmailVerificationRepository(
    EmailVerificationRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, verification: EmailVerification) -> None:
        model = self._to_model(verification)
        self._session.add(model)

    async def update(self, verification: EmailVerification) -> None:
        model = await self._session.get(
            EmailVerificationModel,
            verification.id.value,
        )

        if model is None:
            # raise not found error
            raise RuntimeError

        EmailVerificationORMMapper.update_model(model, verification)

    async def find_by_id(self, verification_id: EmailVerificationId) -> EmailVerification | None:
        stmt = select(EmailVerificationModel).where(
            EmailVerificationModel.id == verification_id.value
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def find_by_user_id(self, user_id: UserId) -> EmailVerification | None:
        stmt = select(EmailVerificationModel).where(EmailVerificationModel.user_id == user_id.value)

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def find_active_token_hash_for_update(
        self,
        token_hash: EmailVerificationTokenHash,
    ) -> EmailVerification | None:
        stmt = (
            select(EmailVerificationModel)
            .where(
                EmailVerificationModel.token_hash == token_hash.value,
            )
            .with_for_update()
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    @property
    def model_type(self) -> type[EmailVerificationModel]:
        return EmailVerificationModel

    def _to_domain(self, model: EmailVerificationModel) -> EmailVerification:
        return EmailVerificationORMMapper.to_domain(model)

    def _to_model(self, entity: EmailVerification) -> EmailVerificationModel:
        return EmailVerificationORMMapper.to_model(entity)
