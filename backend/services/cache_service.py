"""
In-memory caching service for performance optimization.
Caches trending content, embeddings, and recommendations.
"""

from typing import Any, Optional, Dict, Tuple
from datetime import datetime, timedelta
import threading


class CacheService:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self):
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        with self._lock:
            if key not in self._cache:
                return None
            
            value, expiry = self._cache[key]
            
            # Check if expired
            if datetime.utcnow() > expiry:
                del self._cache[key]
                return None
            
            return value
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 5 minutes)
        """
        with self._lock:
            expiry = datetime.utcnow() + timedelta(seconds=ttl)
            self._cache[key] = (value, expiry)
    
    def invalidate(self, key: str):
        """Remove key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_keys = len(self._cache)
            expired_keys = sum(
                1 for _, expiry in self._cache.values()
                if datetime.utcnow() > expiry
            )
            
            return {
                "total_keys": total_keys,
                "active_keys": total_keys - expired_keys,
                "expired_keys": expired_keys
            }


# Singleton instance
cache_service = CacheService()
