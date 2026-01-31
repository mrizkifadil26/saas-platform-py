import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.app_users.user import User


class UserRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        # query = "SELECT * FROM users WHERE id = :user_id"
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query, {"user_id": user_id})

        # return result.fetchone()
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        # query = "SELECT * FROM users WHERE email = :email"
        query = select(User).where(User.email == email)
        result = await self.db.execute(query, {"email": email})

        # return result.fetchone()
        return result.scalar_one_or_none()

    async def create_user(self, email: str, full_name: str | None = None) -> User:
        u = User(email=email, full_name=full_name)

        self.db.add(u)
        await self.db.flush()
        # await self.db.commit()
        # await self.db.refresh(user)

        return u
