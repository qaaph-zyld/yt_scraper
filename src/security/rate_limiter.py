"""
Rate limiting module with token bucket algorithm.
"""
from typing import Dict, Optional
import time
import threading
from dataclasses import dataclass
from loguru import logger
from functools import wraps

@dataclass
class TokenBucket:
    """Token bucket for rate limiting."""
    capacity: int
    refill_rate: float
    tokens: float
    last_refill: float

class RateLimiter:
    """Rate limiter using token bucket algorithm."""
    
    def __init__(self):
        """Initialize rate limiter."""
        self.logger = logger.bind(module="rate_limiter")
        self.buckets: Dict[str, TokenBucket] = {}
        self._lock = threading.Lock()
    
    def create_limit(self, key: str, capacity: int, refill_rate: float = 1.0):
        """Create a new rate limit."""
        with self._lock:
            self.buckets[key] = TokenBucket(
                capacity=capacity,
                refill_rate=refill_rate,
                tokens=float(capacity),
                last_refill=time.time()
            )
            self.logger.info(f"Created rate limit for {key}: {capacity} tokens, {refill_rate}/s")
    
    def _refill_tokens(self, bucket: TokenBucket) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - bucket.last_refill
        new_tokens = elapsed * bucket.refill_rate
        
        bucket.tokens = min(bucket.capacity, bucket.tokens + new_tokens)
        bucket.last_refill = now
    
    def check_limit(self, key: str, tokens: int = 1) -> bool:
        """Check if action is allowed within rate limit."""
        with self._lock:
            bucket = self.buckets.get(key)
            if not bucket:
                self.logger.warning(f"No rate limit defined for {key}")
                return True
            
            self._refill_tokens(bucket)
            
            if bucket.tokens >= tokens:
                bucket.tokens -= tokens
                return True
            
            self.logger.warning(f"Rate limit exceeded for {key}")
            return False
    
    def get_remaining_tokens(self, key: str) -> Optional[float]:
        """Get remaining tokens for a rate limit."""
        with self._lock:
            bucket = self.buckets.get(key)
            if not bucket:
                return None
            
            self._refill_tokens(bucket)
            return bucket.tokens

def rate_limit(key: str, tokens: int = 1):
    """Decorator for rate-limited functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, '_rate_limiter'):
                self._rate_limiter = RateLimiter()
                self._rate_limiter.create_limit(key, capacity=100, refill_rate=10)
            
            if not self._rate_limiter.check_limit(key, tokens):
                raise RateLimitExceeded(f"Rate limit exceeded for {key}")
            
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass
