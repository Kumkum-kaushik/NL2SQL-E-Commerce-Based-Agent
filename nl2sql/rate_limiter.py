import time
import threading
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter with per-minute and per-day limits.
    Thread-safe implementation to prevent API quota exhaustion.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 10,
        requests_per_day: int = 1500
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute
            requests_per_day: Maximum requests allowed per day
        """
        self.rpm_limit = requests_per_minute
        self.rpd_limit = requests_per_day
        
        # Per-minute tracking
        self.minute_tokens = requests_per_minute
        self.minute_last_refill = time.time()
        
        # Per-day tracking
        self.day_tokens = requests_per_day
        self.day_last_refill = time.time()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Statistics
        self.total_requests = 0
        self.total_blocked = 0
        
        logger.info(
            f"Initialized RateLimiter: {requests_per_minute} RPM, "
            f"{requests_per_day} RPD"
        )
    
    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        current_time = time.time()
        
        # Refill per-minute tokens
        minute_elapsed = current_time - self.minute_last_refill
        if minute_elapsed >= 60:
            self.minute_tokens = self.rpm_limit
            self.minute_last_refill = current_time
            logger.debug(f"Refilled minute tokens: {self.minute_tokens}")
        
        # Refill per-day tokens
        day_elapsed = current_time - self.day_last_refill
        if day_elapsed >= 86400:  # 24 hours
            self.day_tokens = self.rpd_limit
            self.day_last_refill = current_time
            logger.debug(f"Refilled day tokens: {self.day_tokens}")
    
    def acquire(self, blocking: bool = False, timeout: Optional[float] = None) -> bool:
        """
        Acquire permission to make a request.
        
        Args:
            blocking: If True, wait until a token is available
            timeout: Maximum time to wait in seconds (only used if blocking=True)
            
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        start_time = time.time()
        
        while True:
            with self._lock:
                self._refill_tokens()
                
                # Check if we have tokens available
                if self.minute_tokens > 0 and self.day_tokens > 0:
                    self.minute_tokens -= 1
                    self.day_tokens -= 1
                    self.total_requests += 1
                    
                    logger.debug(
                        f"Request allowed (minute: {self.minute_tokens}/{self.rpm_limit}, "
                        f"day: {self.day_tokens}/{self.rpd_limit})"
                    )
                    return True
                else:
                    self.total_blocked += 1
                    
                    # Determine which limit was hit
                    limit_type = "minute" if self.minute_tokens <= 0 else "day"
                    logger.warning(
                        f"Rate limit exceeded ({limit_type}): "
                        f"minute={self.minute_tokens}/{self.rpm_limit}, "
                        f"day={self.day_tokens}/{self.rpd_limit}"
                    )
                    
                    if not blocking:
                        return False
            
            # If blocking, check timeout
            if timeout is not None and (time.time() - start_time) >= timeout:
                logger.warning(f"Rate limiter timeout after {timeout}s")
                return False
            
            # Wait a bit before retrying
            time.sleep(1)
    
    def get_wait_time(self) -> float:
        """
        Get estimated wait time in seconds until next request is allowed.
        
        Returns:
            Wait time in seconds
        """
        with self._lock:
            self._refill_tokens()
            
            if self.minute_tokens > 0 and self.day_tokens > 0:
                return 0.0
            
            # Calculate wait time based on which limit was hit
            if self.minute_tokens <= 0:
                minute_wait = 60 - (time.time() - self.minute_last_refill)
                return max(0, minute_wait)
            else:
                day_wait = 86400 - (time.time() - self.day_last_refill)
                return max(0, day_wait)
    
    def get_stats(self) -> dict:
        """
        Get rate limiter statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            self._refill_tokens()
            
            return {
                "total_requests": self.total_requests,
                "total_blocked": self.total_blocked,
                "minute_tokens_remaining": self.minute_tokens,
                "minute_tokens_limit": self.rpm_limit,
                "day_tokens_remaining": self.day_tokens,
                "day_tokens_limit": self.rpd_limit,
                "estimated_wait_seconds": self.get_wait_time()
            }
    
    def reset(self) -> None:
        """Reset all counters and refill tokens."""
        with self._lock:
            self.minute_tokens = self.rpm_limit
            self.day_tokens = self.rpd_limit
            self.minute_last_refill = time.time()
            self.day_last_refill = time.time()
            self.total_requests = 0
            self.total_blocked = 0
            logger.info("Rate limiter reset")


# Global rate limiter instance
_global_limiter: Optional[RateLimiter] = None


def get_rate_limiter(rpm: int = 10, rpd: int = 1500) -> RateLimiter:
    """
    Get or create global rate limiter instance.
    
    Args:
        rpm: Requests per minute
        rpd: Requests per day
        
    Returns:
        Global RateLimiter instance
    """
    global _global_limiter
    
    if _global_limiter is None:
        _global_limiter = RateLimiter(
            requests_per_minute=rpm,
            requests_per_day=rpd
        )
    
    return _global_limiter
