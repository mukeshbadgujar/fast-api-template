from typing import Any, Optional
import redis.asyncio as redis
from app.core.settings import settings
import logging
from functools import wraps
import json
import time

logger = logging.getLogger(__name__)

# In-memory fallback cache
fallback_cache = {}

class Cache:
    def __init__(self):
        self.redis_client = None
        self.use_fallback = settings.REDIS_FALLBACK
        
        if not self.use_fallback:
            try:
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    password=settings.REDIS_PASSWORD,
                    db=settings.REDIS_DB,
                    decode_responses=True,
                )
                logger.info("Successfully connected to Redis")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                self.use_fallback = True
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self.use_fallback:
            return fallback_cache.get(key)
        
        try:
            value = await self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return fallback_cache.get(key)
    
    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in cache."""
        if self.use_fallback:
            fallback_cache[key] = value
            return True
        
        try:
            await self.redis_client.set(
                key,
                json.dumps(value),
                ex=expire
            )
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            fallback_cache[key] = value
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if self.use_fallback:
            fallback_cache.pop(key, None)
            return True
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            fallback_cache.pop(key, None)
            return True

# Global cache instance
cache = Cache()

def cached(expire: int = 3600):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_value = await cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await cache.set(key, result, expire)
            
            return result
        return wrapper
    return decorator 