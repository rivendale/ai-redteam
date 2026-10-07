"""A thread-safe token bucket with an injectable clock."""
import threading
import time


class TokenBucket:
    def __init__(self, capacity, refill_per_sec, clock=time.monotonic):
        if capacity <= 0 or refill_per_sec <= 0:
            raise ValueError("capacity and refill_per_sec must be positive")
        self.capacity = float(capacity)
        self.rate = float(refill_per_sec)
        self._clock = clock
        self._tokens = float(capacity)
        self._last = clock()
        self._lock = threading.Lock()

    def _refill(self, now):
        elapsed = now - self._last
        if elapsed > 0:
            self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
            self._last = now

    def try_acquire(self, n=1):
        """Take n tokens if available; never blocks. Returns True when taken."""
        if n <= 0 or n > self.capacity:
            raise ValueError("n must be in (0, capacity]")
        with self._lock:
            self._refill(self._clock())
            if self._tokens >= n:
                self._tokens -= n
                return True
            return False

    def seconds_until(self, n=1):
        """Seconds until n tokens will be available (0 if available now)."""
        if n <= 0 or n > self.capacity:
            raise ValueError("n must be in (0, capacity]")
        with self._lock:
            self._refill(self._clock())
            missing = n - self._tokens
            return 0.0 if missing <= 0 else missing / self.rate
