from typing import Any, Hashable
import time


class OnCooldown(Exception):
    """Raised when a bucket is on cooldown"""
    def __init__(self, retry_after):
        super().__init__(f"Retry again in {retry_after:.2f}s")
        self.retry_after = retry_after


class Bucket:
    def __init__(self, rate, per, cooldown):
        self.rate = rate
        self.per = per
        self.cooldown = cooldown

        self.times = set()
        self.on_cooldown: bool | float = False

    def _clear_times(self):
        current = time.monotonic()
        self.times = {t for t in self.times if current - t < self.per}
        return self.times

    def add_time(self):
        self._clear_times()
        time_to_add = time.monotonic()

        if self.on_cooldown is not False:
            raise OnCooldown(self.on_cooldown - time_to_add)

        num = sum([time_to_add - t < self.per for t in self.times])
        if num == self.rate - 1:
            self.on_cooldown = time_to_add + self.per
        self.times.add(time_to_add)


class Cooldown:
    def __init__(
            self,
            *,
            rate: int,
            per: int,
    ):
        self._rate = rate
        self._per = per
        self._cache = {}

    def _clean_buckets(self):
        to_remove = set()

        for k, bucket in self._cache.items():
            if not bucket._clear_times():
                to_remove.add(k)

        for k in to_remove:
            del self._cache[k]

    def get_key(self, item: Any) -> Hashable:
        """A function which takes `item` and returns the key to get the button from, can be subclassed"""
        return item

    def get_bucket(self, item: Any) -> Bucket:
        key = self.get_key(item)
        bucket = self._cache.get(key)

        if bucket is None:
            bucket = Bucket(self._rate, self._per, 0)
            self._cache[key] = bucket

        return bucket

    def update_ratelimit(self, item: Any):
        self._clean_buckets()
        bucket = self.get_bucket(item)

        try:
            bucket.add_time()
        except OnCooldown as e:
            return e.retry_after
