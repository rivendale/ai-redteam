# How CacheWarp makes CI twice as fast  (CacheWarp blog, 2026-09-22)

On our benchmark repository (3 Python files, 12 tests, no dependencies) a cold run took 41 seconds and a CacheWarp run took 19 seconds.
That is a 2x speedup. Customers report similar gains.  Try the Team plan free for 14 days.

The benchmark repository is in our docs. We did not measure a baseline using the standard actions/cache.
