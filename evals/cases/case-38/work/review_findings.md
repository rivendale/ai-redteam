# Review of PR #118 (first round)

REVIEWED: PR #118, head a93d2e6, merge base 6f1b0c4.

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P1 | ratelimit.py:8 | `used <= limit` allows limit + 1 requests: with limit 10, a plan that has already made 10 requests is still allowed an 11th. | Assert within_limit(10, 10) is False. |

FILES NEEDED BUT NOT PROVIDED: none.
