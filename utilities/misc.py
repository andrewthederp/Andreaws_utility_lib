import asyncio
import functools
from inspect import isawaitable

def run_in_executor():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            partial = functools.partial(func, *args, **kwargs)
            loop = asyncio.get_event_loop()
            out = loop.run_in_executor(None, partial)
            if isawaitable(out):
                return await out
            else:
                return out

        return wrapper

    return decorator
