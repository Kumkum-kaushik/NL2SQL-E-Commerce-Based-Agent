"""
Test script for rate limiting and caching functionality.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from nl2sql.cache import QueryCache
from nl2sql.rate_limiter import RateLimiter
import time

def test_cache():
    """Test cache functionality."""
    print("=" * 60)
    print("Testing Cache Functionality")
    print("=" * 60)
    
    cache = QueryCache(ttl=5)
    
    # Test cache set and get
    test_prompt = "SELECT * FROM users WHERE id = 1"
    cache.set(test_prompt, "test_response")
    
    result = cache.get(test_prompt)
    assert result == "test_response", "Cache hit failed"
    print("✓ Cache HIT works")
    
    # Test cache miss
    result = cache.get("nonexistent_prompt")
    assert result is None, "Cache miss failed"
    print("✓ Cache MISS works")
    
    # Test cache stats
    stats = cache.get_stats()
    print(f"✓ Cache stats: {stats}")
    assert stats["hits"] == 1, "Hit count incorrect"
    assert stats["misses"] == 1, "Miss count incorrect"
    
    # Test cache expiration
    print("\nWaiting 6 seconds for cache expiration...")
    time.sleep(6)
    result = cache.get(test_prompt)
    assert result is None, "Cache expiration failed"
    print("✓ Cache EXPIRATION works")
    
    print("\n✅ All cache tests passed!\n")


def test_rate_limiter():
    """Test rate limiter functionality."""
    print("=" * 60)
    print("Testing Rate Limiter Functionality")
    print("=" * 60)
    
    limiter = RateLimiter(requests_per_minute=3, requests_per_day=10)
    
    # Test requests within limit
    assert limiter.acquire() == True, "First request failed"
    assert limiter.acquire() == True, "Second request failed"
    assert limiter.acquire() == True, "Third request failed"
    print("✓ Rate limiter allows requests within limit (3/3)")
    
    # Test request over limit
    assert limiter.acquire() == False, "Rate limiter didn't block request"
    print("✓ Rate limiter blocks requests over limit")
    
    # Test stats
    stats = limiter.get_stats()
    print(f"✓ Rate limiter stats: {stats}")
    assert stats["total_requests"] == 3, "Request count incorrect"
    assert stats["total_blocked"] == 1, "Blocked count incorrect"
    
    # Test wait time
    wait_time = limiter.get_wait_time()
    print(f"✓ Estimated wait time: {wait_time:.1f} seconds")
    assert wait_time > 0, "Wait time should be positive"
    
    print("\n✅ All rate limiter tests passed!\n")


if __name__ == "__main__":
    try:
        test_cache()
        test_rate_limiter()
        print("=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
