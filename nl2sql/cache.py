import hashlib
import time
import threading
from typing import Optional, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class QueryCache:
    """
    Thread-safe in-memory cache with TTL (Time To Live) support.
    Caches LLM responses to reduce API calls for identical queries.
    """
    
    def __init__(self, ttl: int = 3600):
        """
        Initialize cache.
        
        Args:
            ttl: Time to live in seconds (default: 1 hour)
        """
        self.ttl = ttl
        self._cache: Dict[str, Tuple[str, float]] = {}
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
        logger.info(f"Initialized QueryCache with TTL={ttl}s")
    
    def _generate_key(self, prompt: str) -> str:
        """Generate cache key from prompt using hash."""
        return hashlib.sha256(prompt.encode()).hexdigest()
    
    def get(self, prompt: str) -> Optional[str]:
        """
        Get cached response for a prompt.
        
        Args:
            prompt: The prompt to look up
            
        Returns:
            Cached response or None if not found/expired
        """
        key = self._generate_key(prompt)
        
        with self._lock:
            if key in self._cache:
                response, timestamp = self._cache[key]
                
                # Check if expired
                if time.time() - timestamp < self.ttl:
                    self._hits += 1
                    logger.info(f"Cache HIT (hits={self._hits}, misses={self._misses})")
                    return response
                else:
                    # Remove expired entry
                    del self._cache[key]
                    logger.debug(f"Cache entry expired for key: {key[:16]}...")
            
            self._misses += 1
            logger.info(f"Cache MISS (hits={self._hits}, misses={self._misses})")
            return None
    
    def set(self, prompt: str, response: str) -> None:
        """
        Store response in cache.
        
        Args:
            prompt: The prompt
            response: The response to cache
        """
        key = self._generate_key(prompt)
        
        with self._lock:
            self._cache[key] = (response, time.time())
            logger.debug(f"Cached response for key: {key[:16]}... (cache size: {len(self._cache)})")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with hits, misses, size, and hit rate
        """
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            
            return {
                "hits": self._hits,
                "misses": self._misses,
                "size": len(self._cache),
                "hit_rate_percent": round(hit_rate, 2)
            }
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        removed = 0
        
        with self._lock:
            expired_keys = [
                key for key, (_, timestamp) in self._cache.items()
                if current_time - timestamp >= self.ttl
            ]
            
            for key in expired_keys:
                del self._cache[key]
                removed += 1
            
            if removed > 0:
                logger.info(f"Cleaned up {removed} expired cache entries")
        
        return removed


# Global cache instance
_global_cache: Optional[QueryCache] = None


def get_cache(ttl: int = 3600) -> QueryCache:
    """
    Get or create global cache instance.
    
    Args:
        ttl: Time to live in seconds
        
    Returns:
        Global QueryCache instance
    """
    global _global_cache
    
    if _global_cache is None:
        _global_cache = QueryCache(ttl=ttl)
    
    return _global_cache
