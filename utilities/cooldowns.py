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

    def get_cooldown(self, key: Hashable) -> float | None:
        return self.cooldowns.get(key)

    def update_cooldown(self, key: Hashable) -> None:
        self.cooldowns[key] = time.monotonic()

    def reset_cooldown(self, key: Hashable) -> bool:
        try:
            del self.cooldowns[key]
            return True
        except KeyError:
            return False

    def on_cooldown(self, key: Hashable) -> bool:
        return time.monotonic() - self.cooldowns.get(key, 0) < self.cooldown

    def get_retry_after(self, key: Hashable) -> float:
        return self.cooldown - (time.monotonic() - self.cooldowns.get(key, 0))


def cooldown(cooldown: int, key_func: Callable):
    def decorator(func):
        cd_obj = Cooldown(cooldown)

        def new_func(*args, **kwargs):
            key = key_func(*args, **kwargs)
            if cd_obj.on_cooldown(key):
                raise OnCooldown(retry_after=cd_obj.get_retry_after(key))

            cd_obj.update_cooldown(key)
            return func(*args, **kwargs)

        new_func.cooldown = cd_obj
        return new_func
    return decorator
