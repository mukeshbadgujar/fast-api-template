from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import asyncio
import logging

from app.core.settings import settings
from app.api.v1.api import api_router
from app.core.logging import configure_logging
from app.core.middleware import RequestLoggingMiddleware
from app.core.tracing import configure_tracing
from app.core.tasks import process_fallback_queue
from app.core.cache import cache
from app.db.session import engine, async_session_factory

logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    # Configure logging
    configure_logging()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Configure OpenTelemetry
    if settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        configure_tracing()
        FastAPIInstrumentor.instrument_app(app)
    
    # Add Prometheus metrics
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    
    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    return app


app = create_application()


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    # Start fallback queue processor if needed
    if settings.CELERY_FALLBACK:
        asyncio.create_task(process_fallback_queue())
        logger.info("Started fallback queue processor")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    # Close database connections
    await engine.dispose()
    
    # Close Redis connection if not in fallback mode
    if not settings.REDIS_FALLBACK and cache.redis_client:
        await cache.redis_client.close()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    status = {
        "status": "healthy",
        "database": "primary" if not settings.DB_FALLBACK else "fallback",
        "cache": "redis" if not settings.REDIS_FALLBACK else "memory",
        "queue": "celery" if not settings.CELERY_FALLBACK else "memory",
    }
    return status 