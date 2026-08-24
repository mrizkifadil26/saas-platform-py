from iam.identity.domain.value_objects import UserId
from iam.sessions.domain import Session
from iam.sessions.domain.value_objects import SessionId

from .models import SessionModel


class SessionORMMapper:
    @staticmethod
    def to_domain(model: SessionModel):
        return Session(
            id=SessionId(model.id),
            user_id=UserId(model.user_id),
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
            last_activity_at=model.last_activity_at,
        )

    @staticmethod
    def to_model(session: Session):
        return SessionModel(
            id=session.id.value,
            user_id=session.user_id.value,
            status=session.status.value,
            expires_at=session.expires_at,
            created_at=session.created_at,
            updated_at=session.updated_at,
            revoked_at=session.revoked_at,
            last_activity_at=session.last_activity_at,
        )

    @staticmethod
    def update_model(
        model: SessionModel,
        session: Session,
    ):
        model.status = session.status
        model.expires_at = session.expires_at
        model.updated_at = session.updated_at
        model.revoked_at = session.revoked_at
        model.last_activity_at = session.last_activity_at
