from sqlalchemy.ext.asyncio import AsyncSession

from db.repo.app_users.api_key_repo import APIKeyRepo
from db.utils.api_keys import hash_token


async def verify_api_key_token(
    db: AsyncSession,
    *,
    token: str,
    pepper: str,
):
    repo = APIKeyRepo(db)
    key_hash = hash_token(
        token=token,
        pepper=pepper,
    )

    return await repo.get_by_hash(key_hash)
