from functools import wraps
from typing import Callable, TypeVar
import hashlib
from app.cache.service import CacheService
import json

T = TypeVar("T")
cache_service = CacheService()


def get_cache_key_from_payload(payload: dict) -> str:
    return f"{hashlib.md5(str(payload).encode()).hexdigest()}"


def cacheable(ttl: int = 3600):
    """
    Decorator to cache the result of a function based on the request payload.
    :param ttl: The time (Seconds) to live for the cache.
    :return: The result of the function.
    NOTE: The function must have a request parameter.
    NOTE: It can be static or dynamic based on the request data.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Get request from kwargs or args
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if hasattr(arg, 'model_dump'):
                        request = arg
                        break

            if request:
                # Create cache key using the template and request data
                try:
                    cache_key = get_cache_key_from_payload(request.model_dump())

                    cached = cache_service.get(cache_key)
                    if cached:
                        print(f"Cache hit: {cache_key}")
                        return json.loads(cached)
                    else:
                        print(f"Cache miss: {cache_key}")
                        result = await func(*args, **kwargs)
                        cache_service.set(cache_key, result.model_dump_json() if hasattr(result, "model_dump_json") else result, ex=ttl)
                        return result
                except KeyError as e:
                    # NOTE Maybe we should raise an error to APM here
                    # If template variables don't match request data, use the template as is
                    print(f"KeyError: {e}")
        return wrapper
    return decorator
