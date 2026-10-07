Implement a token bucket rate limiter in Python: capacity N, refill R tokens per second, thread-safe, with an injectable
clock so it can be tested without sleeping. try_acquire(n) must never block; a method must report how long until n tokens
are available. Include tests.
