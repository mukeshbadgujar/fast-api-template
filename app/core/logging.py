import logging
import sys
from typing import Any, Dict

import structlog
from structlog.types import Processor


def configure_logging() -> None:
    """Configure structured logging for the application."""
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )


class RequestLoggingMiddleware:
    """Middleware for logging HTTP requests and responses."""

    def __init__(self, app):
        self.app = app
        self.logger = structlog.get_logger()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # Log request
        self.logger.info(
            "http.request.start",
            method=scope["method"],
            path=scope["path"],
            query_string=scope["query_string"].decode(),
        )

        # Create a custom send function to log the response
        async def custom_send(message):
            if message["type"] == "http.response.start":
                self.logger.info(
                    "http.response.start",
                    status_code=message["status"],
                )
            elif message["type"] == "http.response.body":
                self.logger.info(
                    "http.response.body",
                )
            await send(message)

        await self.app(scope, receive, custom_send) 