"""
Tests for security modules.
"""
import pytest
import time
from src.security.rate_limiter import RateLimiter, RateLimitExceeded, rate_limit
from src.security.input_validator import (
    InputValidator, ValidationRule, ValidationError, validate_input
)

# Rate Limiter Tests
def test_rate_limiter_basic():
    """Test basic rate limiting functionality."""
    limiter = RateLimiter()
    limiter.create_limit("test", capacity=2, refill_rate=1.0)
    
    assert limiter.check_limit("test")  # First request
    assert limiter.check_limit("test")  # Second request
    assert not limiter.check_limit("test")  # Should be blocked
    
    time.sleep(1.1)  # Wait for refill
    assert limiter.check_limit("test")  # Should work again

def test_rate_limiter_refill():
    """Test token refill mechanism."""
    limiter = RateLimiter()
    limiter.create_limit("test", capacity=1, refill_rate=1.0)
    
    assert limiter.check_limit("test")
    assert not limiter.check_limit("test")
    
    time.sleep(0.5)
    assert not limiter.check_limit("test")  # Not enough time passed
    
    time.sleep(0.6)  # Total 1.1s
    assert limiter.check_limit("test")  # Should have refilled

def test_rate_limiter_decorator():
    """Test rate limit decorator."""
    class TestClass:
        def __init__(self):
            self._rate_limiter = RateLimiter()
            self._rate_limiter.create_limit("test_func", capacity=1, refill_rate=0.5)
        
        @rate_limit("test_func")
        def test_func(self):
            return "success"
    
    obj = TestClass()
    assert obj.test_func() == "success"
    
    with pytest.raises(RateLimitExceeded):
        obj.test_func()
    
    time.sleep(2.1)
    assert obj.test_func() == "success"

# Input Validator Tests
def test_input_validator_basic():
    """Test basic input validation."""
    validator = InputValidator()
    validator.add_rule("test_field", ValidationRule(
        field_type=str,
        min_length=2,
        max_length=5
    ))
    
    # Valid input
    assert not validator.validate({"test_field": "abc"})
    
    # Invalid input
    errors = validator.validate({"test_field": "a"})
    assert len(errors) == 1
    assert "must be at least 2 characters" in errors[0]
    
    errors = validator.validate({"test_field": "abcdef"})
    assert len(errors) == 1
    assert "must be at most 5 characters" in errors[0]

def test_input_validator_pattern():
    """Test pattern validation."""
    validator = InputValidator()
    validator.add_rule("email", ValidationRule(
        field_type=str,
        pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    ))
    
    # Valid email
    assert not validator.validate({"email": "test@example.com"})
    
    # Invalid email
    errors = validator.validate({"email": "invalid-email"})
    assert len(errors) == 1
    assert "does not match required pattern" in errors[0]

def test_input_validator_custom():
    """Test custom validation function."""
    def validate_even(value):
        return isinstance(value, int) and value % 2 == 0
    
    validator = InputValidator()
    validator.add_rule("even_number", ValidationRule(
        field_type=int,
        custom_validator=validate_even
    ))
    
    # Valid even number
    assert not validator.validate({"even_number": 2})
    
    # Invalid odd number
    errors = validator.validate({"even_number": 3})
    assert len(errors) == 1
    assert "failed custom validation" in errors[0]

def test_input_validator_sanitize():
    """Test input sanitization."""
    validator = InputValidator()
    
    # Test basic string sanitization
    input_data = {
        "text": "Hello <script>alert('xss')</script>",
        "nested": {
            "html": "<b>bold</b>"
        },
        "list": ["<i>item</i>", 42]
    }
    
    sanitized = validator.sanitize(input_data)
    
    assert "<script>" not in sanitized["text"]
    assert "<b>" not in sanitized["nested"]["html"]
    assert "<i>" not in sanitized["list"][0]
    assert sanitized["list"][1] == 42

def test_input_validator_decorator():
    """Test validation decorator."""
    validator = InputValidator()
    validator.add_rule("name", ValidationRule(
        field_type=str,
        min_length=2
    ))
    
    class TestClass:
        @validate_input(validator)
        def process(self, name: str):
            return f"Hello, {name}!"
    
    obj = TestClass()
    
    # Valid input
    assert obj.process(name="Bob") == "Hello, Bob!"
    
    # Invalid input
    with pytest.raises(ValidationError) as exc:
        obj.process(name="a")
    assert "must be at least 2 characters" in str(exc.value)
