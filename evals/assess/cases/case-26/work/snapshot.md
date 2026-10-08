# Selecting tests by diff, with numbers  (post, 2026-09-29)

We map each test file to the source files it imports and, on a pull request, run only the tests whose imports intersect the diff. On our repo
(1,900 tests) CI dropped from 31 to 12 minutes. The 40 lines of Python are included below, with the exact commands and our before and after
timings for 20 consecutive PRs. Cost: one stale-map failure in 20 PRs; a nightly full run catches it.
