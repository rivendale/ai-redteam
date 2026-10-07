import threading
import unittest

from token_bucket import TokenBucket


class FakeClock:
    def __init__(self):
        self.t = 100.0

    def __call__(self):
        return self.t


class TokenBucketTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.b = TokenBucket(5, 2, clock=self.clock)

    def test_starts_full(self):
        self.assertTrue(all(self.b.try_acquire() for _ in range(5)))
        self.assertFalse(self.b.try_acquire())

    def test_refills_at_rate(self):
        for _ in range(5):
            self.b.try_acquire()
        self.clock.t += 1.0
        self.assertTrue(self.b.try_acquire(2))
        self.assertFalse(self.b.try_acquire())

    def test_never_exceeds_capacity(self):
        self.clock.t += 1000
        self.assertTrue(self.b.try_acquire(5))
        self.assertFalse(self.b.try_acquire())

    def test_clock_going_backwards_is_ignored(self):
        self.b.try_acquire(5)
        self.clock.t -= 50
        self.assertFalse(self.b.try_acquire())
        self.clock.t += 50.5
        self.assertTrue(self.b.try_acquire())

    def test_seconds_until(self):
        self.b.try_acquire(5)
        self.assertAlmostEqual(self.b.seconds_until(1), 0.5)
        self.assertEqual(self.b.seconds_until(0.0001 + 0) > 0, True)

    def test_bad_arguments(self):
        with self.assertRaises(ValueError):
            TokenBucket(0, 1)
        with self.assertRaises(ValueError):
            self.b.try_acquire(6)

    def test_threads_never_over_issue(self):
        b = TokenBucket(100, 1e-9, clock=lambda: 1.0)
        taken = []

        def worker():
            for _ in range(50):
                if b.try_acquire():
                    taken.append(1)

        ts = [threading.Thread(target=worker) for _ in range(8)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        self.assertEqual(len(taken), 100)


if __name__ == "__main__":
    unittest.main()
