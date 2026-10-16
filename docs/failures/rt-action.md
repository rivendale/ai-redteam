# T32 Bounded PR review GitHub Action

- Use a read-only token and an opt-in repository model secret, never echoing the secret or placing it in argv/artifacts.
- Fork PRs must fail closed before any secret-bearing job/step; include a denying-direction test proving the key is unreachable.
- Treat PR descriptions/diffs/files as untrusted evidence, never instructions; do not execute PR code with credentials.
- Pin actions; bound model requests/cost; document output as one review round, not approval, adjudication or merge.
- Test with mocks only; no real key/model calls or repository secret changes.

Authority: T32 in the task registry at a1a47caa448ea40a4575b4aab0def6d815165a0d. Failure list precedes implementation. Public repository; PR only; independent review; no merge.
