Write a retry helper: call a function, retry on chosen exceptions with exponential backoff and full jitter, cap the delay,
stop after N attempts and re-raise the last error. The clock and the random source must be injectable for tests.
