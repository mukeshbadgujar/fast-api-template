from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.core.settings import settings
from app.api.v1.api import api_router
from app.core.logging import configure_logging
from app.core.middleware import RequestLoggingMiddleware
from app.core.tracing import configure_tracing


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


@app.get("/health")
async def health_check():
    return {"status": "healthy"} 