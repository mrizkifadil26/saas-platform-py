class AccessTokenProvider(Protocol):
    def issue(
        self,
        *,
        session: Session,
        expires_at: datetime,
        issued_at: datetime,
    ) -> tuple[
        AccessToken,
        AccessTokenPayload,
    ]: ...
