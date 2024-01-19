import asyncio
import functools

def run_in_executor(func):
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        f = functools.partial(func, *args, **kwargs)
        out = await loop.run_in_executor(None, f)
        return await out

    return wrapper
