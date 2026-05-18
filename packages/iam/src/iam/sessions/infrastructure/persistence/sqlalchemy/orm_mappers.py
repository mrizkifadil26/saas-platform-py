from iam.identity.domain.value_objects import UserId
from iam.sessions.domain import RefreshToken, Session
from iam.sessions.domain.value_objects import RefreshTokenHash, SessionId

from .models import RefreshTokenModel, SessionModel


class SessionORMMapper:
    @staticmethod
    def to_domain(model: SessionModel):
        refresh_tokens = [
            RefreshToken(
                token_hash=RefreshTokenHash(token.token_hash),
                expires_at=token.expires_at,
                created_at=token.created_at,
                revoked_at=token.revoked_at,
                replaced_by_token_hash=RefreshTokenHash(token.replaced_by_token_hash)
                if token.replaced_by_token_hash
                else None,
            )
            for token in model.refresh_tokens
        ]

        return Session(
            id=SessionId(model.id),
            user_id=UserId(model.user_id),
            refresh_tokens=refresh_tokens,
            created_at=model.created_at,
            updated_at=model.updated_at,
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
            last_activity_at=model.last_activity_at,
        )

    @staticmethod
    def to_model(session: Session):
        refresh_token_models = [
            RefreshTokenModel(
                token_hash=token.token_hash.value,
                session_id=session.id.value,
                expires_at=token.expires_at,
                created_at=token.created_at,
                revoked_at=token.revoked_at,
                replaced_by_token_hash=token.replaced_by_token_hash.value
                if token.replaced_by_token_hash
                else None,
            )
            for token in session.refresh_tokens
        ]

        return SessionModel(
            id=session.id.value,
            user_id=session.user_id.value,
            status=session.status.value,
            expires_at=session.expires_at,
            created_at=session.created_at,
            updated_at=session.updated_at,
            revoked_at=session.revoked_at,
            last_activity_at=session.last_activity_at,
            refresh_tokens=refresh_token_models,
        )

    @staticmethod
    def update_model(
        model: SessionModel,
        session: Session,
    ):
        refresh_token_models = [
            RefreshTokenModel(
                token_hash=token.token_hash.value,
                session_id=session.id.value,
                expires_at=token.expires_at,
                created_at=token.created_at,
                revoked_at=token.revoked_at,
                replaced_by_token_hash=(
                    token.replaced_by_token_hash.value
                    if token.replaced_by_token_hash
                    else None
                ),
            )
            for token in session.refresh_tokens
        ]

        model.status = session.status
        model.expires_at = session.expires_at
        model.updated_at = session.updated_at
        model.revoked_at = session.revoked_at
        model.last_activity_at = session.last_activity_at

        model.refresh_tokens.clear()
        model.refresh_tokens.extend(
            refresh_token_models,
        )
