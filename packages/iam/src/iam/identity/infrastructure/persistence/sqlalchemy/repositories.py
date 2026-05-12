from sqlalchemy import func, select

from db.repositories import SQLAlchemyRepository
from iam.identity.domain import User, UserRepository
from iam.identity.domain.value_objects import EmailAddress, UserId

from .models import UserModel
from .orm_mappers import UserORMMapper


class SQLAlchemyUserRepository(
    SQLAlchemyRepository[User, UserModel],
    UserRepository,
):
    async def save(self, user: User) -> None:
        existing = await self._session.get(UserModel, user.id)
        if existing is None:
            model = self._to_model(user)
            self._session.add(model)
            return

        UserORMMapper.update_model(existing, user)

    async def find_by_id(self, user_id: UserId) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id.value)

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def find_by_email(self, email: EmailAddress) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email.value)

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def list(self, *, limit: int, offset: int) -> tuple[list[User], int]:
        users_stmt = (
            select(UserModel)
            .order_by(UserModel.created_at.desc())
            .limit(limit)
            .offset(offset)
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
