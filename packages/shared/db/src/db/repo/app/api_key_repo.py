import uuid
from datetime import datetime, timezone

from packages.shared.db.src.db.models.app.api_key import APIKey
from sqlalchemy import select, update


class APIKeyRepo:
    def __init__(self, db):
        self.db = db

    async def create_api_key(
        self,
        *,
        workspace_id: uuid.UUID,
        name: str,
        key_hash: str,
        last4: str,
        created_by_user_id: uuid.UUID | None = None,
    ) -> APIKey:
        api_key = APIKey(
            workspace_id=workspace_id,
            name=name,
            key_hash=key_hash,
            last4=last4,
            created_by_user_id=created_by_user_id,
        )

        self.db.add(api_key)
        await self.db.flush()
        return api_key

    async def list_api_keys(
        self,
        workspace_id: uuid.UUID,
        *,
        included_revoked: bool = False,
    ) -> list[APIKey]:
        stmt = select(APIKey).where(APIKey.workspace_id == workspace_id)
        if not included_revoked:
            stmt = stmt.where(APIKey.revoked_at.is_(None))

        stmt = stmt.order_by(APIKey.created_at.desc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_by_hash(self, key_hash: str) -> APIKey | None:
        stmt = (
            select(APIKey)
            .where(APIKey.key_hash == key_hash)
            .where(APIKey.revoked_at.is_(None))
            .limit(1)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def revoke_api_key(self, api_key: APIKey) -> bool:
        now = datetime.now(timezone.utc)
        stmt = (
            update(APIKey)
            .where(
                APIKey.id == api_key.id,
                APIKey.revoked_at.is_(None),
            )
            .values(revoked_at=now)
            .returning(APIKey.id)
        )

        res = await self.db.execute(stmt)
        return res.scalar_one_or_none() is not None
