from sqlalchemy import select

from db.repositories import SQLAlchemyRepository
from iam.authentication.domain import Credential, CredentialRepository
from iam.identity.domain.value_objects import UserId

from .models import CredentialModel
from .orm_mappers import (
    CredentialORMMapper,
)


class SQLAlchemyCredentialRepository(
    SQLAlchemyRepository[Credential, CredentialModel],
    CredentialRepository,
):
    @property
    def model_type(self) -> type[CredentialModel]:
        return CredentialModel

    def _to_domain(self, model: CredentialModel) -> Credential:
        return CredentialORMMapper.to_domain(model)

    def _to_model(self, entity: Credential) -> CredentialModel:
        return CredentialORMMapper.to_model(entity)

    async def save(
        self,
        credential: Credential,
    ) -> None:
        existing_model = await self._session.get(
            CredentialModel,
            credential.id.value,
        )

        if existing_model is None:
            model = self._to_model(credential)
            self._session.add(model)
            return

        CredentialORMMapper.update_model(
            existing_model,
            credential,
        )

    async def find_by_user_id(
        self,
        user_id: UserId,
    ) -> Credential | None:
        stmt = select(CredentialModel).where(
            CredentialModel.user_id == user_id.value,
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)
