import os
from datetime import datetime, timezone
from threading import Lock


class DailyRateLimiter:
    def __init__(self, limit: int):
        self.limit = limit
        self._lock = Lock()
        self._window = ""
        self._counts: dict[str, int] = {}

    def try_acquire(self, key: str) -> bool:
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with self._lock:
            if self._window != day:
                self._window = day
                self._counts = {}
            count = self._counts.get(key, 0)
            if count >= self.limit:
                return False
            self._counts[key] = count + 1
            return True


tailor_limiter = DailyRateLimiter(limit=int(os.getenv("TAILOR_DAILY_LIMIT", "3")))


def check_tailor_limit(ip: str, device_id: str) -> bool:
    key = f"{ip}|{device_id or 'unknown'}"
    return tailor_limiter.try_acquire(key)