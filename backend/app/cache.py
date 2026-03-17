import asyncio
import logging
import json
import hashlib
import time
from typing import Optional, Any, Dict
from app.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        # Simple in-memory cache as fallback when Redis is not available
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.redis_available = False

        # Try to connect to Redis, but don't fail if it's not available
        try:
            import redis.asyncio as redis
            self.redis = redis.from_url(settings.redis_url, decode_responses=True)
            self.redis_available = True
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory cache: {str(e)}")
            self.redis_available = False

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self.redis_available:
            try:
                value = await self.redis.get(key)
                if value:
                    return json.loads(value)
                return None
            except Exception as e:
                logger.error(f"Redis get failed: {str(e)}")
                return None
        else:
            # In-memory cache
            if key in self.cache:
                entry = self.cache[key]
                if time.time() < entry['expires']:
                    return entry['value']
                else:
                    del self.cache[key]
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        if self.redis_available:
            try:
                await self.redis.setex(key, ttl, json.dumps(value))
                return True
            except Exception as e:
                logger.error(f"Redis set failed: {str(e)}")
                return False
        else:
            # In-memory cache
            self.cache[key] = {
                'value': value,
                'expires': time.time() + ttl
            }
            return True

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get failed: {str(e)}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        try:
            await self.redis.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Cache set failed: {str(e)}")
            return False

    def _generate_cache_key(self, image_bytes: Optional[bytes], text_query: Optional[str]) -> str:
        """Generate a unique cache key for search requests."""
        content = ""
        if image_bytes:
            content += hashlib.md5(image_bytes).hexdigest()
        if text_query:
            content += text_query
        return f"search:{hashlib.md5(content.encode()).hexdigest()}"

    async def get_search_cache(self, image_bytes: Optional[bytes], text_query: Optional[str]) -> Optional[dict]:
        """Get cached search results."""
        key = self._generate_cache_key(image_bytes, text_query)
        return await self.get(key)

    async def set_search_cache(self, image_bytes: Optional[bytes], text_query: Optional[str], results: dict) -> bool:
        """Cache search results."""
        key = self._generate_cache_key(image_bytes, text_query)
        return await self.set(key, results, ttl=1800)  # 30 minutes

cache_service = CacheService()