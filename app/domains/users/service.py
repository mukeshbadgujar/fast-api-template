from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.domains.users.models import User
from app.domains.users.schemas import UserCreate, UserUpdate
from app.domains.users.repository import UserRepository


class UserService:
    """User service for business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UserRepository(db)

    async def get(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return await self.repository.get(user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return await self.repository.get_by_email(email)

    async def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users."""
        return await self.repository.list(skip, limit)

    async def create(self, user_in: UserCreate) -> User:
        """Create a new user."""
        user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=get_password_hash(user_in.password),
            is_active=user_in.is_active,
            is_superuser=user_in.is_superuser,
        )
        return await self.repository.create(user)

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

        return await self.repository.update(user)

    async def delete(self, user_id: int) -> None:
        """Delete a user."""
        await self.repository.delete(user_id) 