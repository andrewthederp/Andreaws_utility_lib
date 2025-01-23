import time
from typing import Hashable, Callable


class OnCooldown(Exception):
    """An exception raised when the function is on cooldown"""

    def __init__(self, *, retry_after):
        self.retry_after = retry_after


class Cooldown:
    def __init__(self, cooldown: int):
        self.cooldown = cooldown
        self.cooldowns: dict[Hashable, float] = {}

    def get_cooldown(self, key: Hashable):
        return self.cooldowns.get(key)

    def update_cooldown(self, key: Hashable):
        self.cooldowns[key] = time.monotonic()

    def on_cooldown(self, key: Hashable):
        return time.monotonic() - self.cooldowns.get(key, 0) < self.cooldown

    def get_retry_after(self, key: Hashable):
        return self.cooldown - (time.monotonic() - self.cooldowns.get(key, 0))


def cooldown(cooldown: int, key_func: Callable = None):
    def decorator(func):
        cd_obj = Cooldown(cooldown)

        def new_func(*args, **kwargs):
            key = key_func(*args, **kwargs)
            if cd_obj.on_cooldown(key):
                raise OnCooldown(retry_after=cd_obj.get_retry_after(key))

            cd_obj.update_cooldown(key)
            return func(*args, **kwargs)
        return new_func
    return decorator
