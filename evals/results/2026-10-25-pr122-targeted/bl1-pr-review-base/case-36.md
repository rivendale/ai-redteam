# PR #131 Review: audit record on cancellation

## Review report

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs are short forms taken from PR.md. I could not verify them, because I had no tools and no checkout in this session. I reviewed the supplied `change.patch` against `work/base/`. If the real head differs from that patch, this review does not cover it.

**TIER:** Standard. The change adds audit logging to an ordinary code path, and the context marks the stakes as standard. It does not touch auth, permissions, secrets, migrations or money movement. One caveat: the change writes signed-in user ids into a new log. If the owner treats those ids as personal data, the tier becomes High, and a second round on another approved reviewer is still required.

**REVIEWERS:**
- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), a separate instance that did not write the change. No code left this session.
- Author: unknown. No commits or `Co-Authored-By` trailers were provided.

**Not run:** I had no execution environment, so the "Tests pass" claim is unverified. Reading the tests, I expect all five to pass. For example, `open()` in a missing directory raises `FileNotFoundError`, which is a subclass of `OSError`.

**Scope check:** The change does what was asked. It records the event and the actor using the shared library, adds nothing beyond that, and threads the signed-in user's id through the handler. The design choice to write the audit record before the status change is sound for "no cancellation without a record". It creates the opposite gap, described in F1.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P2 | `orders.py:16-17` (`record(...)` then `db.set_status(...)`) | `record` succeeds, then `db.set_status` raises (DB timeout, lost connection). The audit log says `order.cancelled` by the actor, but the order is still open. Support and finance see a cancellation that never happened. If the user retries and it succeeds, the log holds two `order.cancelled` lines for one cancellation. The docstring promises "never made without its record" but says nothing about records without a cancellation. | `FakeDb` whose `set_status` raises `RuntimeError`. Call `cancel_order` and assert the error propagates. Then assert the log does not contain an unqualified `order.cancelled` for `o1`. A fix could record a compensating `order.cancel_failed` event, or record intent and outcome separately. This test fails today. |
| F2 | P2 | `orders.py:9-17` (read status, then record, then set, with no lock or conditional update) | Two concurrent requests, for example a double-click or a user and a support agent, both read `status == "open"`. Both write `order.cancelled`, possibly with different actors, and both set the status. The PR claims "cancelling … already cancelled … records nothing", but that only holds for sequential calls. The audit trail then shows two cancellers for one order. | `FakeDb` whose `get_order` returns `open` on both calls, interleaving two `cancel_order` calls before either `set_status`. Assert exactly one audit line, which fails today. A fix would use a conditional update (`UPDATE … WHERE status='open'`, checking rows affected) or a row lock before recording. |
| F3 | P3 | `tests/test_orders.py:51-53` (`test_cancelling_twice_records_once`) | The test name claims "twice", but it only cancels an order that starts out cancelled. It never runs open → cancel → cancel. A regression that writes a record on the second call of a real double cancel would pass if the fake started in the open state. | Cancel with a `FakeDb("open")` that updates its own status in `set_status`. Cancel again, then assert the log has exactly one line. |
| F4 | P3 | `tests/test_orders.py:27-32` (`test_cancel_is_on_disk_before_it_returns`) | The test name and PR.md claim durability ("on disk"), but the test only re-reads the file, which works from the page cache. It does not show that `fsync` happens. If `os.fsync` were removed from `company_audit.record`, the test would still pass. | Patch `os.fsync` with a mock and assert it is called once per `record`. Or rename the test to match what it checks. |
| F5 | P3 | `company_audit.py:13` (`open(AUDIT_PATH, "a")` + `fsync(f)`, no directory fsync) | The first cancellation after deployment or log rotation creates `audit.log`. The file's data is fsynced, but the directory entry is not. On a crash right afterwards, the file can vanish on some filesystems, losing a record for an order that `set_status` already cancelled. This is in the shared library and outside this PR's diff. It matters only because the PR relies on "writes and fsyncs before it returns" as its durability guarantee. | Hard to unit-test. Mock `os.open`/`os.fsync` and assert the parent directory is fsynced when the file is newly created. Or log it as a library issue. |

### FILES NEEDED BUT NOT PROVIDED
- **Rest of the repository:** needed to confirm PR.md's claim that `handlers.cancel` is the only caller of `cancel_order`. The signature now requires `actor`, so any other caller, such as an admin tool, batch job or other test, now raises `TypeError`.
- **Login middleware:** needed to confirm `request["user"]` is always set on this route. If it is missing, the handler now raises `KeyError` (500) where it used to succeed.
- **Real `db` implementation:** needed to judge whether F2 can actually happen, for example whether `get_order` locks the row.
- **CI check results and the commit list with trailers.**

## Close-out

This section is not written yet. Adjudication belongs to the author and whoever closes the PR, and a reviewer does not adjudicate its own findings.

**ADJUDICATION:** pending for F1–F5. All five are P2 or P3, so each can be Accepted, Deferred with a tracking issue, or Rejected with evidence.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION:** Not yet. I found no P0 or P1 blockers, and the core behavior matches the request. Step 8 still fails on three counts:
- No finding has a written decision yet.
- I have not seen any CI checks, and a missing check is not green.
- The caller-coverage question above is open.

Once F1–F5 are decided (F1 and F2 should at least be deferred to tracked issues, since finance relies on this trail), checks are green, and no other callers of `cancel_order` are confirmed, I would expect a merge recommendation.

```json
{
  "verdict": "not yet: no blockers found; pending written adjudication of F1-F5, CI checks, and confirmation of no other cancel_order callers",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds, then db.set_status raises; audit log shows order.cancelled for an order still open; a retry adds a second record",
      "fix": "Record a compensating/failed event when set_status raises, or record intent and outcome separately; add a test with a FakeDb whose set_status raises"
    },
    {
      "severity": "P2",
      "evidence_level": "code-read (depends on real db, not provided)",
      "location": "orders.py:9-17",
      "scenario": "Two concurrent cancels both read status open and both write order.cancelled, possibly with different actors",
      "fix": "Use a conditional update (WHERE status='open', check rows affected) or a row lock before recording; add an interleaving test asserting one audit line"
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py:51-53",
      "scenario": "test_cancelling_twice_records_once never cancels twice; a regression on a real double cancel would go undetected",
      "fix": "Cancel an open order twice with a stateful FakeDb and assert exactly one audit line"
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py:27-32",
      "scenario": "The test claims on-disk durability but only re-reads the file; removing os.fsync would still pass",
      "fix": "Mock os.fsync and assert it is called, or rename the test"
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "company_audit.py:13",
      "scenario": "A newly created audit.log's directory entry is not fsynced; after a crash the first record can be lost while the order is cancelled",
      "fix": "fsync the parent directory when the file is created (shared library change; may be tracked separately)"
    }
  ]
}
```