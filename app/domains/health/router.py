from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.domains.health.schemas import HealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Check the health of the application."""
    # Check database connection
    await db.execute("SELECT 1")
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
    ) 