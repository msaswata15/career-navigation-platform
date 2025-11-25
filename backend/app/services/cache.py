"""
Redis caching for API responses
"""

import redis.asyncio as redis
import json
from typing import Any, Optional

class RedisCache:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        """Cache value with expiration"""
        await self.redis.setex(
            key,
            expire,
            json.dumps(value)
        )
    
    async def delete(self, key: str):
        """Delete cached value"""
        await self.redis.delete(key)
