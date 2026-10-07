"""Rate limiting middleware."""
import time


class RateLimiter:
    def __init__(self, limit=100, window=60, clock=time.monotonic):
        self.limit, self.window, self.clock = limit, window, clock
        self._hits = {}

    def allow(self, request):
        """request has .remote_addr (str) and .user_id (str or None)."""
        key = request.remote_addr
        now = self.clock()
        hits = [t for t in self._hits.get(key, []) if now - t < self.window]
        if len(hits) >= self.limit:
            self._hits[key] = hits
            return False
        hits.append(now)
        self._hits[key] = hits
        return True
