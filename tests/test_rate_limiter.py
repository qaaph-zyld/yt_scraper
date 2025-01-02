import pytest
import time
import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.rate_limiter import RateLimiter

@pytest.fixture
def rate_limiter():
    """Create a RateLimiter instance with test quotas."""
    quotas = {
        'queries_per_second': {'tokens': 2, 'interval': 1},
        'queries_per_minute': {'tokens': 10, 'interval': 60}
    }
    return RateLimiter(quotas)

def test_rate_limiter_initialization(rate_limiter):
    """Test that the rate limiter initializes with correct quotas."""
    status = rate_limiter.get_quota_status()
    assert 'queries_per_second' in status
    assert 'queries_per_minute' in status
    assert status['queries_per_second']['max_tokens'] == 2
    assert status['queries_per_minute']['max_tokens'] == 10

def test_token_acquisition(rate_limiter):
    """Test basic token acquisition."""
    # Should be able to acquire tokens immediately
    assert rate_limiter.acquire(tokens=1)
    assert rate_limiter.acquire(tokens=1)
    # Should fail to acquire more tokens (exceeded per-second quota)
    assert not rate_limiter.acquire(tokens=1, timeout=0)

def test_token_refill(rate_limiter):
    """Test that tokens are refilled after the interval."""
    # Use up all tokens
    assert rate_limiter.acquire(tokens=1)
    assert rate_limiter.acquire(tokens=1)
    assert not rate_limiter.acquire(tokens=1, timeout=0)
    
    # Wait for refill
    time.sleep(1.1)  # Wait slightly longer than 1 second
    
    # Should be able to acquire tokens again
    assert rate_limiter.acquire(tokens=1)

def test_multiple_quotas(rate_limiter):
    """Test that multiple quotas are enforced correctly."""
    # Use up per-second quota
    assert rate_limiter.acquire(tokens=2)
    assert not rate_limiter.acquire(tokens=1, timeout=0)
    
    # Wait for per-second quota to refill
    time.sleep(1.1)
    
    # Should be able to acquire more tokens
    for _ in range(8):  # Already used 2, can use 8 more within the minute
        assert rate_limiter.acquire(tokens=1)
    
    # Should hit the per-minute quota
    assert not rate_limiter.acquire(tokens=1, timeout=0)

def test_quota_status(rate_limiter):
    """Test that quota status is reported correctly."""
    initial_status = rate_limiter.get_quota_status()
    assert initial_status['queries_per_second']['available_tokens'] == 2
    assert initial_status['queries_per_minute']['available_tokens'] == 10
    
    # Use some tokens
    rate_limiter.acquire(tokens=1)
    
    updated_status = rate_limiter.get_quota_status()
    assert updated_status['queries_per_second']['available_tokens'] < 2
    assert updated_status['queries_per_minute']['available_tokens'] < 10
