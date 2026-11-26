from collections import defaultdict, deque
from threading import Lock
from time import monotonic


class SlidingWindowLimiter:
    def __init__(self, maximum: int, window_seconds: int):
        self.maximum = maximum
        self.window_seconds = window_seconds
        self._attempts: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str, now: float | None = None) -> bool:
        moment = monotonic() if now is None else now
        with self._lock:
            attempts = self._attempts[key]
            threshold = moment - self.window_seconds
            while attempts and attempts[0] <= threshold:
                attempts.popleft()
            if len(attempts) >= self.maximum:
                return False
            attempts.append(moment)
            return True

    def reset(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)
