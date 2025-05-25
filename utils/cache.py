#!/usr/bin/env python
# coding: utf-8

"""
Caching utilities for the cognitive warfare dashboard.
"""

import logging
import time
from typing import Any, Dict, Optional
from functools import wraps

# Simple in-memory cache
_cache = {}
_cache_timestamps = {}

def clear_cache():
    """Clear all cached data."""
    global _cache, _cache_timestamps
    _cache.clear()
    _cache_timestamps.clear()
    logging.info("Cache cleared")

def cache_result(timeout: int = 3600):
    """
    Decorator to cache function results.
    
    Args:
        timeout: Cache timeout in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # Check if result is cached and not expired
            if cache_key in _cache:
                timestamp = _cache_timestamps.get(cache_key, 0)
                if time.time() - timestamp < timeout:
                    logging.debug(f"Cache hit for {func.__name__}")
                    return _cache[cache_key]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            _cache[cache_key] = result
            _cache_timestamps[cache_key] = time.time()
            logging.debug(f"Cache miss for {func.__name__}, result cached")
            
            return result
        return wrapper
    return decorator

def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics.
    
    Returns:
        Dict[str, Any]: Cache statistics
    """
    return {
        'total_entries': len(_cache),
        'memory_usage_mb': sum(len(str(v)) for v in _cache.values()) / (1024 * 1024),
        'oldest_entry': min(_cache_timestamps.values()) if _cache_timestamps else None,
        'newest_entry': max(_cache_timestamps.values()) if _cache_timestamps else None
    }