from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.domains.users.dependencies import (
    get_current_active_user,
    get_current_superuser,
    get_current_user,
)
from app.domains.users.models import User

# Re-export common dependencies for use in API routes
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
CurrentSuperUser = Annotated[User, Depends(get_current_superuser)] 