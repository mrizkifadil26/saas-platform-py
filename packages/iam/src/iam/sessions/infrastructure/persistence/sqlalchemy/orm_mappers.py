from iam.identity.domain.value_objects import UserId
from iam.sessions.domain import Session
from iam.sessions.domain.value_objects import SessionId

from .models import SessionModel


class SessionORMMapper:
    @staticmethod
    def to_model(session: Session):
        return SessionModel(
            id=session.id.value,
            user_id=session.user_id.value,
            token_hash=session.token_hash,
            revoked=session.revoked,
            created_at=session.created_at,
            expires_at=session.expires_at,
        )

    @staticmethod
    def to_domain(model: SessionModel):
        return Session(
            id=SessionId(model.id),
            user_id=UserId(model.user_id),
            token_hash=model.token_hash,
            revoked=model.revoked,
            created_at=model.created_at,
            expires_at=model.expires_at,
        )

    @staticmethod
    def update_model(
        model: SessionModel,
        session: Session,
    ):
        model.user_id = session.user_id.value
        model.token_hash = session.token_hash
        model.revoked = session.revoked
        model.created_at = session.created_at
        model.expires_at = session.expires_at
