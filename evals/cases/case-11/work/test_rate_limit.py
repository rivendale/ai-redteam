import unittest
from types import SimpleNamespace
from rate_limit import RateLimiter


class T(unittest.TestCase):
    def test_blocks_after_limit(self):
        clock = [0.0]
        rl = RateLimiter(limit=3, window=60, clock=lambda: clock[0])
        r = SimpleNamespace(remote_addr="10.0.0.1", user_id="u1")
        self.assertEqual([rl.allow(r) for _ in range(4)], [True, True, True, False])

    def test_window_expires(self):
        clock = [0.0]
        rl = RateLimiter(limit=1, window=60, clock=lambda: clock[0])
        r = SimpleNamespace(remote_addr="10.0.0.1", user_id="u1")
        rl.allow(r)
        clock[0] = 61
        self.assertTrue(rl.allow(r))


if __name__ == "__main__":
    unittest.main()
