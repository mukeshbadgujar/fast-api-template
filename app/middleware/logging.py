import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        
        # Log request details
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None,
            },
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time * 1000, 2),
                },
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
        except Exception as e:
            # Log exception
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "process_time_ms": round((time.time() - start_time) * 1000, 2),
                },
                exc_info=True,
            )
            raise 