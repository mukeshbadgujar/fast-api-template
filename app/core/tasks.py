from celery import Celery
from app.core.settings import settings
import logging
import asyncio
from typing import Any, Callable, Dict, Optional
from functools import wraps

logger = logging.getLogger(__name__)

# In-memory fallback queue
fallback_queue = []
fallback_results = {}

class TaskQueue:
    def __init__(self):
        self.celery_app = None
        self.use_fallback = settings.CELERY_FALLBACK
        
        if not self.use_fallback:
            try:
                self.celery_app = Celery(
                    "fastapi_template",
                    broker=settings.CELERY_BROKER_URL,
                    backend=settings.CELERY_RESULT_BACKEND,
                )
                logger.info("Successfully connected to Celery")
            except Exception as e:
                logger.warning(f"Failed to connect to Celery: {e}")
                self.use_fallback = True
    
    async def delay(self, task_name: str, *args, **kwargs) -> str:
        """Delay a task for execution."""
        if self.use_fallback:
            task_id = f"fallback_{len(fallback_queue)}"
            fallback_queue.append((task_id, task_name, args, kwargs))
            return task_id
        
        try:
            task = self.celery_app.send_task(task_name, args=args, kwargs=kwargs)
            return task.id
        except Exception as e:
            logger.error(f"Celery delay error: {e}")
            task_id = f"fallback_{len(fallback_queue)}"
            fallback_queue.append((task_id, task_name, args, kwargs))
            return task_id
    
    async def get_result(self, task_id: str) -> Optional[Any]:
        """Get task result."""
        if task_id.startswith("fallback_"):
            return fallback_results.get(task_id)
        
        try:
            result = self.celery_app.AsyncResult(task_id)
            return result.get() if result.ready() else None
        except Exception as e:
            logger.error(f"Celery get_result error: {e}")
            return fallback_results.get(task_id)

# Global task queue instance
task_queue = TaskQueue()

def task(name: Optional[str] = None):
    """Decorator for creating tasks."""
    def decorator(func: Callable):
        task_name = name or func.__name__
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if task_queue.use_fallback:
                # Execute task immediately in fallback mode
                result = await func(*args, **kwargs)
                task_id = f"fallback_{len(fallback_queue)}"
                fallback_results[task_id] = result
                return result
            
            return await task_queue.delay(task_name, *args, **kwargs)
        
        return wrapper
    return decorator

async def process_fallback_queue():
    """Process tasks in the fallback queue."""
    while True:
        if fallback_queue:
            task_id, task_name, args, kwargs = fallback_queue.pop(0)
            try:
                # Find and execute the task function
                task_func = globals().get(task_name)
                if task_func:
                    result = await task_func(*args, **kwargs)
                    fallback_results[task_id] = result
            except Exception as e:
                logger.error(f"Error processing fallback task {task_name}: {e}")
        
        await asyncio.sleep(1)  # Prevent CPU spinning 