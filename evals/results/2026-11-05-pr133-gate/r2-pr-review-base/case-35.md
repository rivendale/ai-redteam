# pr-review report: PR #131, audit record on cancellation

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs are as stated in PR.md. I had no git access, so I could not confirm them. Only the supplied files were reviewed: `PR.md`, `change.patch`, and `base/{README.md,handlers.py,orders.py}`.

**TIER:** Standard. The change adds a write to the audit trail and reorders the cancellation flow. It touches no auth, secrets, money movement or personal data (the actor is an opaque user id). One model round.

**REVIEWERS:** This instance (Claude Sonnet 5.5) reviewed it, with no memory of writing the change. The author is unknown because no commit trailers were supplied. Data protection (Step 3): only order ids and user ids are in scope, and nothing was sent to any other endpoint.

**Not done:** I did not run the tests. The claim "Tests pass" is unverified. Reading them, they look consistent with the code. They stub the shared library, so they say nothing about the real one.

**Request check:** The request asked for an audit record of who cancelled, using the shared library. The patch does that, with no extra behavior. The wording in PR.md and the docstring matches the enforced behavior:
- A failed audit write leaves the order open.
- An already-cancelled order records nothing.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | The audit is written before `set_status`. If `set_status` raises (DB error or timeout), the audit trail holds `order.cancelled` for an order that is still open. A retry then writes a second record. Support and finance would read a cancellation that never happened. The docstring's "never made without its record" covers only the opposite direction. | Fake DB whose `set_status` raises. Cancel, then retry. Assert that the audit never says "cancelled" for an open order, or that the pair is idempotent and de-duplicated. |
| 2 | P2 | `orders.py:9-17` | There is a check-then-act race. Two concurrent requests both read `open`, both pass the cancelled check, and both call `record`. The audit then holds two records for one cancellation, possibly with different actors. "Cancelling twice records once" holds only for sequential calls. No lock or transaction is visible. I could not see `db`, so this is inferred. | Two threads cancel the same order through a DB fake with a barrier after `get_order`. Assert exactly one audit record. |
| 3 | P2 | `tests/test_orders.py:14` (and `orders.py:2,16`) | The tests replace `company_audit` in `sys.modules` with a stub that accepts any kwargs. A wrong event name, wrong field names or a wrong signature in the real library would pass every test. If the real `record` has a different contract, every cancellation fails in production. The stub also leaks into any other test module in the same process. | Contract test against the real library, or `create_autospec(company_audit.record)`, asserting the call binds to the real signature. |
| 4 | P3 | `handlers.py:7`, `orders.py:16` | `request["user"]` is read directly. If the middleware leaves it missing, the result is a `KeyError` (a 500, no cancel, so it fails closed). If it is `""` or `None`, a record with no actor is written, which defeats the purpose. | Handler test with `user` absent, `""` and `None`. Assert no cancel and no record, or an explicit 401. |
| 5 | P3 | `orders.py:2` | `company_audit` is imported at module top. If it is not installed or declared as a dependency in the deployed environment, importing `orders` fails and takes the whole service down. No manifest or lockfile was provided, so I cannot tell whether it is declared. | Import test in a clean environment built from the declared dependencies. |

**Coverage gap (not a finding):** The real `company_audit.record` was not provided. Its signature, accepted fields, failure behavior (raise vs. swallow), and whether it is transactional with the DB are all UNVERIFIED. The PR's central guarantee ("a failed audit write leaves the order open") holds only if `record` raises on failure. The tests prove it only for a stub that does.

**"Only caller" claim:** Within the supplied files, `handlers.cancel` is the only caller. I could not search the rest of the repository, so the claim is UNVERIFIED beyond that.

**FILES NEEDED BUT NOT PROVIDED:**
- `company_audit` (module source or its documented contract)
- the DB layer (`get_order` / `set_status`, transaction semantics)
- the dependency manifest or lockfile
- the login middleware
- a repo-wide caller search for `cancel_order`

**Next step:** Close-out (adjudication of each finding by the author, with verification of any fix commits) is not part of this report. My preliminary view is "merge after fixes." The condition is that the `company_audit` contract is confirmed and finding 3 is addressed, with findings 1 and 2 fixed or deferred with tracking issues.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "read-code",
      "location": "orders.py:16-17",
      "scenario": "Audit record is written before set_status. If set_status raises, the trail says order.cancelled for an order still open, and a retry writes a duplicate record.",
      "fix": "Write audit and status change in one transaction, or make the record idempotent keyed by order_id and de-duplicate on retry. Add a test where set_status raises."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred",
      "location": "orders.py:9-17",
      "scenario": "Concurrent cancels of the same open order both pass the status check and both call record, producing duplicate audit entries for one cancellation.",
      "fix": "Make the status transition atomic (conditional update or row lock) and record only for the request that wins it. Add a two-thread test."
    },
    {
      "severity": "P2",
      "evidence_level": "read-code",
      "location": "tests/test_orders.py:14",
      "scenario": "company_audit is stubbed via sys.modules with a permissive fake, so a signature or field mismatch with the real library passes all tests and could break every cancellation in production. The stub also leaks across test modules.",
      "fix": "Add a contract test against the real library or an autospec of the real record signature; scope the stub with unittest.mock.patch.dict instead of a global assignment."
    },
    {
      "severity": "P3",
      "evidence_level": "read-code",
      "location": "handlers.py:7",
      "scenario": "A missing user key raises KeyError (500), and an empty or None user writes an audit record with no actor.",
      "fix": "Validate that request['user'] is a non-empty string before cancelling; return 401 otherwise. Add tests for missing, empty and None."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified",
      "location": "orders.py:2",
      "scenario": "Top-level import of company_audit breaks import of orders, and therefore the service, if the library is not declared and installed in the deployed environment. No manifest was provided to check.",
      "fix": "Confirm company_audit is declared in the dependency manifest, and add a clean-environment import check."
    }
  ]
}
```