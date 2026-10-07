"""Retry with exponential backoff and full jitter."""
import random
import time


def retry(fn, *, attempts=5, base=0.1, cap=5.0, retry_on=(Exception,), sleep=time.sleep, rng=random.random):
    """Call fn() until it returns; re-raise the last error after `attempts` tries.

    Only exceptions in `retry_on` are retried; anything else propagates at once. The delay before try k+1 is a random
    number in [0, min(cap, base * 2**k)] (full jitter).
    """
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    last = None
    for k in range(attempts):
        try:
            return fn()
        except retry_on as e:  # noqa: PERF203
            last = e
            if k == attempts - 1:
                break
            sleep(rng() * min(cap, base * (2 ** k)))
    raise last
