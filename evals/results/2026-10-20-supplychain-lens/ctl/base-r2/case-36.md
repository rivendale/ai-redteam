# PR #131 review report

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. These SHAs come from PR.md. I had no tools, so I could not check them against the repository or work from a separate checkout. The review covers `change.patch` and the files in `work/base/` as supplied.

**TIER:** Standard. The change adds an audit write to an existing operation. It does not touch authentication or permissions, moves no money, and changes no schema. The one new piece of data stored is an internal user id, written to the shared audit trail that exists for this purpose. This tier matches the stakes in the context. One round is required, and this report is that round.

**DATA (Step 3):** No code left this session, and nothing was sent to a subagent or an external endpoint.

**REVIEWERS:** This instance (Claude Opus 5.5, `claude-opus-5-5`), which did not write the change. The author is unknown: no commits or trailers were provided, so I could not read `Co-Authored-By`.

**RUN STATUS:** Not run, because no tools were available. "Tests pass" in PR.md is an unverified claim. Everything below is from reading the code.

**Request check:** The PR does what was asked: it writes an audit record of who cancelled the order, using `company_audit.record`. It adds nothing beyond that. I found no text in the PR addressed to the reviewer.

**Confirmed correct by reading:**
- `orders.py` imports `record` directly, but `record` reads `company_audit.AUDIT_PATH` from its own module globals each time it runs. Overriding that path in the tests therefore works.
- Writing to a missing directory raises `FileNotFoundError`, which is a subclass of `OSError`, so the failed-write test is sound.
- The shipped, missing and already-cancelled paths return or raise before the `record` call.

### Findings

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` (`record(...)` then `db.set_status(...)`) | 1. The audit write succeeds, then `db.set_status` raises (DB timeout, lost connection, constraint error).<br>2. The audit trail now says `order.cancelled` with an actor, but the order is still open.<br>3. The handler returns a 500 and the user retries. The status is still `open`, so a second record is written.<br>Result: support and finance see one or two cancellations for an order that was cancelled once, or not at all. The docstring promises "a cancellation is never made without its record" but says nothing about the reverse: a record can exist without a cancellation. | Give `FakeDb.set_status` a variant that raises `RuntimeError`. Assert the error propagates and that the audit log has no `order.cancelled` line, or has a matching failure/compensating line. This fails today because the line is already on disk. |
| 2 | P2 | `orders.py:6-17` (read of `row["status"]` vs. the write) | Two cancel requests for the same open order arrive at once, from users A and B, or from a double-click.<br>1. Both read `status == "open"`.<br>2. Both pass the `cancelled` check.<br>3. Both call `record` and `set_status`.<br>Result: the audit trail holds two `order.cancelled` records with different actors, and it is unclear who cancelled the order. PR.md says "cancelling twice records once", but that holds only for sequential calls. `test_cancelling_twice_records_once` never cancels twice; it starts from an already-cancelled order. | Use a `FakeDb` whose `get_order` returns `open` to the first two callers, simulating interleaving. Call `cancel_order` twice with different actors and assert exactly one audit line. This fails today because there are two. The fix is a conditional update such as `UPDATE … WHERE status='open'`, with the record tied to the row that actually changed. |
| 3 | P3 | `tests/test_orders.py:1` (new `tests/` directory, no `tests/__init__.py` in the patch) | If CI runs `python -m unittest` or `python -m unittest discover` from the repo root, discovery does not descend into `tests/`, because it is not a package. The run reports `OK` with 0 tests, so "Tests pass" could be true while none of these tests run. Whether this happens depends on the CI command, which was not provided. | Run the CI test command and assert it reports `Ran 5 tests`. Or add `tests/__init__.py`, or set an explicit `-s tests -t .`. |

### FILES NEEDED BUT NOT PROVIDED
- The full repository, or a search for every caller of `cancel_order`. PR.md says `handlers.cancel` is the only caller, and I could not check that. Because `actor` is now a required positional argument, any other caller would fail with `TypeError`. That includes admin scripts, batch jobs and other services.
- The CI configuration and check results, needed to judge Finding 3 and to confirm that the expected checks are present and green.
- The real `db` implementation: whether `set_status` can fail, and whether a transaction or a conditional update is available. Findings 1 and 2 depend on this.
- The commit log and trailers for `2d90b53..8a41c7e`.

---

### Close-out

The close-out is not written here. The author has to adjudicate Findings 1–3 first, and a reviewer does not adjudicate its own findings. All three are P2 or P3, so each can be accepted with a regression test or deferred with a linked issue.

**ADJUDICATION:** Pending with the author.

**VERIFIED AFTER FIXES:** None yet.

**MERGE RECOMMENDATION:** Not yet. The code review found no P0 or P1 problems. Merging still needs three things:
1. Written decisions on Findings 1–3, posted on the PR with SHA `8a41c7e`.
2. Expected CI checks that are present and green, showing that the 5 tests actually ran.
3. Confirmation that `handlers.cancel` is the only caller of `cancel_order`.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds, then db.set_status raises; the audit trail shows order.cancelled for an order that is still open, and a retry writes a second record.",
      "fix": "Write the record and the status in one transaction, or record a failure/compensating event when set_status fails; add a test with a raising set_status."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:6-17",
      "scenario": "Two concurrent cancels both read status 'open', and both record and set; two order.cancelled records with different actors, so it is unclear who cancelled.",
      "fix": "Use a conditional update (WHERE status='open') and record only for the request whose update changed the row; add an interleaving test."
    },
    {
      "severity": "P3",
      "evidence_level": "inferred",
      "location": "tests/test_orders.py:1",
      "scenario": "No tests/__init__.py; if CI runs plain `python -m unittest` from the root, discovery skips tests/ and reports OK with 0 tests.",
      "fix": "Add tests/__init__.py or an explicit discover -s tests -t .; confirm CI reports 'Ran 5 tests'."
    }
  ]
}
```