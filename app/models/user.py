from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """User model."""

    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<User {self.email}>" 