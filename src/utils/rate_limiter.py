import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from loguru import logger
from threading import Lock

class RateLimiter:
    """Rate limiter using token bucket algorithm with multiple quotas."""
    
    def __init__(self, quotas: Dict[str, Dict[str, int]]):
        """
        Initialize rate limiter with quotas.
        
        Args:
            quotas: Dictionary of quota configs, e.g.,
                {
                    'queries_per_day': {'tokens': 10000, 'interval': 86400},
                    'queries_per_second': {'tokens': 10, 'interval': 1}
                }
        """
        self.quotas = {}
        self.last_refill = {}
        self.tokens = {}
        self.locks = {}
        
        for quota_name, config in quotas.items():
            self.quotas[quota_name] = config
            self.tokens[quota_name] = config['tokens']
            self.last_refill[quota_name] = time.time()
            self.locks[quota_name] = Lock()
    
    def _refill_tokens(self, quota_name: str) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill[quota_name]
        config = self.quotas[quota_name]
        
        # Calculate tokens to add based on elapsed time
        new_tokens = (elapsed / config['interval']) * config['tokens']
        self.tokens[quota_name] = min(
            config['tokens'],  # Cap at max tokens
            self.tokens[quota_name] + new_tokens
        )
        self.last_refill[quota_name] = now
    
    def acquire(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Acquire tokens from all quotas. Returns True if successful, False if timeout reached.
        
        Args:
            tokens: Number of tokens to acquire
            timeout: Maximum time to wait in seconds (None for no timeout)
            
        Returns:
            bool: True if tokens were acquired, False if timeout reached
        """
        start_time = time.time()
        
        while True:
            can_acquire = True
            acquired_locks = []
            
            try:
                # Try to acquire all locks
                for quota_name in self.quotas:
                    if not self.locks[quota_name].acquire(blocking=False):
                        # Release any acquired locks
                        for lock in acquired_locks:
                            lock.release()
                        can_acquire = False
                        break
                    acquired_locks.append(self.locks[quota_name])
                
                if not can_acquire:
                    # If we couldn't acquire all locks, wait and retry
                    time.sleep(0.1)
                    if timeout and (time.time() - start_time) > timeout:
                        return False
                    continue
                
                # Check if we have enough tokens in all quotas
                for quota_name in self.quotas:
                    self._refill_tokens(quota_name)
                    if self.tokens[quota_name] < tokens:
                        can_acquire = False
                        break
                
                # If we have enough tokens, consume them
                if can_acquire:
                    for quota_name in self.quotas:
                        self.tokens[quota_name] -= tokens
                    return True
                
                # If we don't have enough tokens, wait and retry
                if timeout and (time.time() - start_time) > timeout:
                    return False
                
                # Wait for a short time before retrying
                time.sleep(0.1)
                
            finally:
                # Always release locks
                for lock in acquired_locks:
                    lock.release()
    
    def get_quota_status(self) -> Dict[str, Dict[str, float]]:
        """Get current status of all quotas."""
        status = {}
        for quota_name in self.quotas:
            with self.locks[quota_name]:
                self._refill_tokens(quota_name)
                status[quota_name] = {
                    'available_tokens': self.tokens[quota_name],
                    'max_tokens': self.quotas[quota_name]['tokens'],
                    'refill_interval': self.quotas[quota_name]['interval']
                }
        return status
