# -------------------------------------
# ✅ FILE: utils/simple_cache.py
# -------------------------------------

import time
from functools import wraps

# A very simple in-memory cache
cache_store = {}

def simple_cache(ttl_seconds=600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (func.__name__, args, frozenset(kwargs.items()))
            cached = cache_store.get(key)

            if cached:
                value, expiry = cached
                if time.time() < expiry:
                    return value
                else:
                    del cache_store[key]

            result = func(*args, **kwargs)
            cache_store[key] = (result, time.time() + ttl_seconds)
            return result

        return wrapper
    return decorator
