from sqlalchemy import select

from db.repositories import SQLAlchemyRepository
from iam.authentication.domain import Credential, CredentialRepository, CredentialType
from iam.identity.domain.value_objects import EmailAddress, UserId
from iam.identity.infrastructure.persistence.sqlalchemy.models import UserModel

from .models import CredentialModel
from .orm_mappers import (
    CredentialORMMapper,
)


class SQLAlchemyCredentialRepository(
    SQLAlchemyRepository[Credential, CredentialModel],
    CredentialRepository,
):
    async def save(self, credential: Credential) -> None:
        existing = await self._session.get(CredentialModel, credential.id)
        if existing is None:
            model = self._to_model(credential)
            self._session.add(model)
            return

        CredentialORMMapper.update_model(existing, credential)

    async def find_password_by_email(
        self,
        email: EmailAddress,
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
