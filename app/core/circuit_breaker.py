from datetime import datetime, timedelta
from typing import Any, Callable, Optional, TypeVar

from tenacity import (
    RetryError,
    retry,
    stop_after_attempt,
    wait_exponential,
)

T = TypeVar("T")


class CircuitBreaker:
    """Circuit breaker pattern implementation."""

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: int = 60,
        retry_count: int = 3,
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.retry_count = retry_count
        self.failures = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open

    def _can_execute(self) -> bool:
        """Check if the circuit breaker can execute the operation."""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            if self.last_failure_time is None:
                return False
            
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.reset_timeout):
                self.state = "half-open"
                return True
            
            return False
        
        # half-open state
        return True

    def _record_failure(self) -> None:
        """Record a failure and update the circuit breaker state."""
        self.failures += 1
        self.last_failure_time = datetime.now()
        
        if self.failures >= self.failure_threshold:
            self.state = "open"

    def _record_success(self) -> None:
        """Record a success and reset the circuit breaker."""
        self.failures = 0
        self.state = "closed"

    async def execute(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute a function with circuit breaker protection."""
        if not self._can_execute():
            raise CircuitBreakerError("Circuit breaker is open")

        @retry(
            stop=stop_after_attempt(self.retry_count),
            wait=wait_exponential(multiplier=1, min=4, max=10),
        )
        async def _execute() -> Any:
            try:
                result = await func(*args, **kwargs)
                self._record_success()
                return result
            except Exception as e:
                self._record_failure()
                raise e

        try:
            return await _execute()
        except RetryError as e:
            raise CircuitBreakerError(f"Operation failed after {self.retry_count} retries") from e


class CircuitBreakerError(Exception):
    """Circuit breaker specific exception."""
    pass 