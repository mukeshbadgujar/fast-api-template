from fastapi import APIRouter

from app.domains.users.router import router as users_router
from app.domains.health.router import router as health_router

api_router = APIRouter()

# Include domain routers
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(users_router, prefix="/users", tags=["users"]) 