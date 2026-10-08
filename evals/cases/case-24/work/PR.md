# PR #41: retry gateway timeouts on capture
Head 3f2a9c1, merge base 77be0d4.

Customers see failed checkouts when the payment gateway times out. This retries `capture` up to three times with a short
backoff. Tests added and passing.
