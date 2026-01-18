"""L2 Redis cache with graceful degradation."""

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, L2 cache disabled")


class L2Cache:
    """Redis-based L2 cache with graceful degradation."""

    def __init__(self, redis_url: Optional[str] = None, ttl_seconds: int = 3600):
        """Initialize L2 cache.

        Args:
            redis_url: Redis connection URL (default: redis://localhost:6379/0)
            ttl_seconds: Time to live in seconds (default: 3600 = 1 hour)
        """
        self.ttl_seconds = ttl_seconds
        self._redis: Optional[Any] = None
        self._enabled = False

        if not REDIS_AVAILABLE:
            logger.warning("Redis library not installed, L2 cache disabled")
            return

        try:
            redis_url = redis_url or "redis://localhost:6379/0"
            self._redis = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self._redis.ping()
            self._enabled = True
            logger.info("L2 cache (Redis) enabled")
        except Exception as e:
            logger.warning(f"Redis connection failed, L2 cache disabled: {e}")
            self._redis = None
            self._enabled = False

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        if not self._enabled or not self._redis:
            return None

        try:
            data = self._redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning(f"L2 cache get failed: {e}")
        return None

    def set(self, key: str, value: Any) -> None:
        """Set value in Redis cache with TTL."""
        if not self._enabled or not self._redis:
            return

        try:
            data = json.dumps(value)
            self._redis.setex(key, self.ttl_seconds, data)
        except Exception as e:
            logger.warning(f"L2 cache set failed: {e}")

    def clear(self) -> None:
        """Clear all cache entries (use with caution)."""
        if not self._enabled or not self._redis:
            return

        try:
            self._redis.flushdb()
        except Exception as e:
            logger.warning(f"L2 cache clear failed: {e}")

    def stats(self) -> dict:
        """Get cache statistics."""
        if not self._enabled or not self._redis:
            return {"enabled": False}

        try:
            info = self._redis.info("memory")
            return {
                "enabled": True,
                "keys": self._redis.dbsize(),
                "ttl_seconds": self.ttl_seconds,
                "memory_used_mb": info.get("used_memory_human", "N/A"),
            }
        except Exception as e:
            logger.warning(f"L2 cache stats failed: {e}")
            return {"enabled": False, "error": str(e)}
