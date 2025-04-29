from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.base import Base
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """User service for CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users."""
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, user_in: UserCreate) -> User:
        """Create a new user."""
        user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=get_password_hash(user_in.password),
            is_active=user_in.is_active,
            is_superuser=user_in.is_superuser,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: int, user_in: UserUpdate) -> User:
        """Update a user."""
        user = await self.get(user_id)
        if not user:
            return None

        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: int) -> None:
        """Delete a user."""
        user = await self.get(user_id)
        if user:
            await self.db.delete(user)
            await self.db.commit() 