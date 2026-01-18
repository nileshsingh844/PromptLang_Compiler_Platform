"""L1 in-memory cache with LRU and TTL."""

import time
from collections import OrderedDict
from typing import Any, Optional


class L1Cache:
    """In-memory LRU cache with TTL support."""

    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        """Initialize L1 cache.

        Args:
            max_size: Maximum number of entries (default: 100)
            ttl_seconds: Time to live in seconds (default: 300 = 5 minutes)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key not in self._cache:
            return None

        value, expiry = self._cache[key]
        if time.time() > expiry:
            del self._cache[key]
            return None

        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return value

    def set(self, key: str, value: Any) -> None:
        """Set value in cache with TTL."""
        expiry = time.time() + self.ttl_seconds

        if key in self._cache:
            # Update existing
            self._cache[key] = (value, expiry)
            self._cache.move_to_end(key)
        else:
            # Add new
            if len(self._cache) >= self.max_size:
                # Remove least recently used
                self._cache.popitem(last=False)

            self._cache[key] = (value, expiry)

    def clear(self) -> None:
        """Clear all entries."""
        self._cache.clear()

    def stats(self) -> dict:
        """Get cache statistics."""
        # Remove expired entries
        now = time.time()
        expired = [k for k, (_, expiry) in self._cache.items() if now > expiry]
        for k in expired:
            del self._cache[k]

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
        }
