from sqlalchemy import select, update

from db.repositories import SQLAlchemyRepository
from iam.sessions.domain import Session, SessionRepository

from .models import SessionModel
from .orm_mappers import SessionORMMapper


class SQLAlchemySessionRepository(
    SQLAlchemyRepository[Session, SessionModel],
    SessionRepository,
):
    async def save(self, session: Session) -> None:
        existing_model = await self._session.get(
            SessionModel,
            session.id.value,
        )

        if existing_model is None:
            model = self._to_model(session)
            self._session.add(model)
            return

        SessionORMMapper.update_model(
            existing_model,
            session,
        )

    async def get_by_token_hash(self, token_hash: str) -> Session | None:
        stmt = select(SessionModel).where(
            SessionModel.token_hash == token_hash,
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None

        return self._to_domain(model)

    async def revoke(self, session_id: str) -> None:
        stmt = (
            update(SessionModel)
            .where(
                SessionModel.id == session_id,
            )
            .values(revoked=True)
        )

        await self._session.execute(stmt)

    @property
    def model_type(self) -> type[SessionModel]:
        return SessionModel

    def _to_domain(self, model: SessionModel) -> Session:
        return SessionORMMapper.to_domain(model)

    def _to_model(self, entity: Session) -> SessionModel:
        return SessionORMMapper.to_model(entity)
