from db.repo.app.types import SupportsRepoSession


class AsyncRepository:
    def __init__(self, db: SupportsRepoSession) -> None:
        self.db = db
