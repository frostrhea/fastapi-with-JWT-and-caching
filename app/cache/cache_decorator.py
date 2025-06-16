import functools
import json
from hashlib import md5
from .cache_config import cache, ENABLE_CACHE

def make_cache_key(func_name, args, kwargs):
    raw_key = json.dumps({"func": func_name, "args": args, "kwargs": kwargs}, sort_keys=True)
    return f"{func_name}:{md5(raw_key.encode()).hexdigest()}"

def cached(ttl: int = 60):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not settings.ENABLE_CACHE:
                return await func(*args, **kwargs)

            # Filter out non-serializable arguments
            filtered_args = [arg for arg in args if isinstance(arg, (int, str, float, bool))]
            filtered_kwargs = {k: v for k, v in kwargs.items() if isinstance(v, (int, str, float, bool))}

            key = make_cache_key(func.__name__, filtered_args, filtered_kwargs)
            if not key:
                return await func(*args, **kwargs)

            cached_result = await cache.get(key)
            if cached_result:
                print(f"Cache hit for key: {key}")
                return json.loads(cached_result)

            print(f"Cache miss for key: {key}")
            result = await func(*args, **kwargs)
            await cache.set(key, json.dumps(result, default=default_json), ttl=ttl)
            return result
        return wrapper
    return decorator