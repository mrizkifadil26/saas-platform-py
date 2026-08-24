from datetime import datetime

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from iam.authentication.domain import (
    AuthenticationAttempt,
    AuthenticationAttemptRepository,
    AuthenticationOutcome,
    Credential,
    CredentialRepository,
    CredentialType,
)
from iam.identity.domain.value_objects import Email, UserId
from iam.identity.infrastructure.persistence.database.models import UserModel

from .models import AuthenticationAttemptModel, CredentialModel
from .orm_mappers import (
    AuthenticationAttemptORMMapper,
    CredentialORMMapper,
)


class SQLAlchemyCredentialRepository(
    CredentialRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, credential: Credential) -> None:
        existing = await self._session.get(CredentialModel, credential.id)
        if existing is None:
            model = self._to_model(credential)
            self._session.add(model)
            return

        CredentialORMMapper.update_model(existing, credential)

    async def find_password_by_email(
        self,
        email: Email,
    ) -> Credential | None:
        stmt = (
            select(CredentialModel)
            .join(
                UserModel,
                CredentialModel.user_id == UserModel.id,
            )
            .where(
                UserModel.email == email.value,
                CredentialModel.type == CredentialType.PASSWORD,
            )
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def find_by_user_and_type(
        self, user_id: UserId, credential_type: CredentialType
    ) -> Credential | None:
        stmt = select(CredentialModel).where(
            CredentialModel.user_id == user_id.value,
            CredentialModel.type == credential_type,
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    @property
    def model_type(self) -> type[CredentialModel]:
        return CredentialModel

    def _to_domain(self, model: CredentialModel) -> Credential:
        return CredentialORMMapper.to_domain(model)

    def _to_model(self, entity: Credential) -> CredentialModel:
        return CredentialORMMapper.to_model(entity)


class SQLAlchemyAuthenticationAttemptRepository(
    AuthenticationAttemptRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, attempt: AuthenticationAttempt) -> None:
        model = self._to_model(attempt)
        self._session.add(model)

    async def list_recent_by_user_id(
        self,
        user_id: UserId,
        limit: int = 10,
    ) -> list[AuthenticationAttempt]:
        stmt = (
            select(AuthenticationAttemptModel)
            .where(AuthenticationAttemptModel.user_id == user_id.value)
            .order_by(desc(AuthenticationAttemptModel.attempted_at))
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def count_recent_failures(
        self,
        *,
        email: Email,
        since: datetime,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(AuthenticationAttemptModel)
            .where(
                AuthenticationAttemptModel.email == email.value,
                AuthenticationAttemptModel.outcome == AuthenticationOutcome.DENIED,
                AuthenticationAttemptModel.attempted_at >= since,
            )
        )

        result = await self._session.execute(stmt)

        return int(result.scalar_one())

    @property
    def model_type(self) -> type[AuthenticationAttemptModel]:
        return AuthenticationAttemptModel

    def _to_domain(self, model: AuthenticationAttemptModel) -> AuthenticationAttempt:
        return AuthenticationAttemptORMMapper.to_domain(model)

    def _to_model(self, entity: AuthenticationAttempt) -> AuthenticationAttemptModel:
        return AuthenticationAttemptORMMapper.to_model(entity)
