from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.domains.users.schemas import User, UserCreate, UserUpdate
from app.domains.users.service import UserService
from app.domains.users.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=List[User])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[User]:
    """List users."""
    service = UserService(db)
    return await service.list(skip=skip, limit=limit)


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Create a new user."""
    service = UserService(db)
    return await service.create(user_in)


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get a user by ID."""
    service = UserService(db)
    user = await service.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Update a user."""
    service = UserService(db)
    user = await service.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return await service.update(user_id, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a user."""
    service = UserService(db)
    user = await service.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    await service.delete(user_id) 