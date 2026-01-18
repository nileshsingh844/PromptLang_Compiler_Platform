"""Cache manager coordinating L1 and L2 caches."""

import logging
from typing import Any, Optional

from promptlang.core.cache.l1_cache import L1Cache
from promptlang.core.cache.l2_cache import L2Cache

logger = logging.getLogger(__name__)


class CacheManager:
    """Unified cache manager with L1 (in-memory) and L2 (Redis) tiers."""

    def __init__(
        self,
        l1_max_size: int = 100,
        l1_ttl: int = 300,
        l2_redis_url: Optional[str] = None,
        l2_ttl: int = 3600,
    ):
        """Initialize cache manager.

        Args:
            l1_max_size: L1 cache max entries
            l1_ttl: L1 cache TTL in seconds
            l2_redis_url: Redis URL for L2 (optional)
            l2_ttl: L2 cache TTL in seconds
        """
        self.l1 = L1Cache(max_size=l1_max_size, ttl_seconds=l1_ttl)
        self.l2 = L2Cache(redis_url=l2_redis_url, ttl_seconds=l2_ttl)

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (L1 first, then L2)."""
        # Try L1 first
        value = self.l1.get(key)
        if value is not None:
            logger.debug(f"Cache hit L1: {key[:16]}...")
            return value

        # Try L2
        value = self.l2.get(key)
        if value is not None:
            logger.debug(f"Cache hit L2: {key[:16]}...")
            # Promote to L1
            self.l1.set(key, value)
            return value

        logger.debug(f"Cache miss: {key[:16]}...")
        return None

    def set(self, key: str, value: Any) -> None:
        """Set value in both L1 and L2 caches."""
        self.l1.set(key, value)
        self.l2.set(key, value)

    def clear(self) -> None:
        """Clear both caches."""
        self.l1.clear()
        self.l2.clear()

    def stats(self) -> dict:
        """Get statistics from both caches."""
        return {
            "l1": self.l1.stats(),
            "l2": self.l2.stats(),
        }
