from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from iam.identity.domain.value_objects import UserId
from iam.sessions.domain import Session, SessionRepository, SessionStatus
from iam.sessions.domain.value_objects import RefreshTokenHash, SessionId

from .models import RefreshTokenModel, SessionModel
from .orm_mappers import SessionORMMapper


class SQLAlchemySessionRepository(
    SessionRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

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

    async def find_by_id(
        self,
        session_id: SessionId,
    ) -> Session | None:
        stmt = (
            select(SessionModel)
            .options(
                selectinload(
                    SessionModel.refresh_tokens,
                )
            )
            .where(SessionModel.id == session_id.value)
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None

        return self._to_domain(model)

    async def find_by_token_hash(
        self,
        token_hash: RefreshTokenHash,
    ) -> Session | None:
        stmt = (
            select(SessionModel)
            .join(RefreshTokenModel)
            .options(
                selectinload(
                    SessionModel.refresh_tokens,
                )
            )
            .where(
                RefreshTokenModel.token_hash == token_hash.value,
            )
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None

        return self._to_domain(model)

    async def find_active_by_user_id(
        self,
        user_id: UserId,
    ) -> list[Session]:
        stmt = (
            select(SessionModel)
            .options(
                selectinload(
                    SessionModel.refresh_tokens,
                )
            )
            .where(
                SessionModel.user_id == user_id.value,
            )
            .where(SessionModel.status == SessionStatus.ACTIVE)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [SessionORMMapper.to_domain(model) for model in models]

    @property
    def model_type(self) -> type[SessionModel]:
        return SessionModel

    def _to_domain(self, model: SessionModel) -> Session:
        return SessionORMMapper.to_domain(model)

    def _to_model(self, entity: Session) -> SessionModel:
        return SessionORMMapper.to_model(entity)
