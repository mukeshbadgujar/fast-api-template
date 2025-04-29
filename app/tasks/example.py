from app.core.celery import celery_app
from app.core.circuit_breaker import CircuitBreaker


@celery_app.task(name="example_task")
def example_task(x: int, y: int) -> int:
    """Example task that adds two numbers."""
    return x + y


@celery_app.task(name="example_task_with_circuit_breaker")
async def example_task_with_circuit_breaker(url: str) -> dict:
    """Example task that uses circuit breaker pattern."""
    circuit_breaker = CircuitBreaker()
    
    async def fetch_data():
        # Simulate external API call
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    
    return await circuit_breaker.execute(fetch_data) 