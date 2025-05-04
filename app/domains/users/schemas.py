from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class UserUpdate(UserBase):
    """User update schema."""
    password: Optional[str] = None


class User(UserBase):
    """User response schema."""
    id: int

    class Config:
        from_attributes = True 