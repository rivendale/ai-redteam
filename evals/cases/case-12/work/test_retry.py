import unittest
from retry import retry


class Flaky:
    def __init__(self, fail_times, exc=ConnectionError):
        self.calls, self.fail_times, self.exc = 0, fail_times, exc

    def __call__(self):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise self.exc("boom %d" % self.calls)
        return "ok"


class RetryTests(unittest.TestCase):
    def test_succeeds_after_failures(self):
        f, slept = Flaky(2), []
        self.assertEqual(retry(f, sleep=slept.append, rng=lambda: 1.0, base=1, cap=100), "ok")
        self.assertEqual(slept, [1, 2])

    def test_gives_up_and_raises_last_error(self):
        f = Flaky(10)
        with self.assertRaises(ConnectionError) as cm:
            retry(f, attempts=3, sleep=lambda s: None)
        self.assertEqual(f.calls, 3)
        self.assertIn("boom 3", str(cm.exception))

    def test_does_not_sleep_after_the_last_attempt(self):
        slept = []
        with self.assertRaises(ConnectionError):
            retry(Flaky(10), attempts=3, sleep=slept.append, rng=lambda: 1.0)
        self.assertEqual(len(slept), 2)

    def test_non_matching_exception_propagates_immediately(self):
        f = Flaky(5, exc=KeyError)
        with self.assertRaises(KeyError):
            retry(f, retry_on=(ConnectionError,), sleep=lambda s: None)
        self.assertEqual(f.calls, 1)

    def test_cap_applies(self):
        slept = []
        with self.assertRaises(ConnectionError):
            retry(Flaky(10), attempts=6, base=1, cap=3, sleep=slept.append, rng=lambda: 1.0)
        self.assertEqual(slept, [1, 2, 3, 3, 3])

    def test_zero_attempts_rejected(self):
        with self.assertRaises(ValueError):
            retry(lambda: 1, attempts=0)


if __name__ == "__main__":
    unittest.main()
