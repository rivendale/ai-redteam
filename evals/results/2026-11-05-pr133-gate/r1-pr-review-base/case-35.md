# Review report: PR #131, audit record on cancellation

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs are taken from PR.md. I had no git repository, so I could not confirm them against history. I reviewed `change.patch` against the files in `base/`.

**TIER:** Standard. The change touches ordinary order logic and an audit write, not auth, money movement, migrations or secrets. Stakes are stated as standard in context.md. The actor id is passed to a library I cannot see, so I could not assess its data handling.

**REVIEWERS:** A fresh reviewer instance (Sonnet 5.5) with no part in writing the change. The author is not identifiable: no commit trailers were provided. No code left this session.

**Not run:** I have no tools, so I did not run the tests. "Tests pass" in the PR is an unverified claim. The tests also stub `company_audit`, so a pass says nothing about the real library.

**Checked against the request:** The change records who cancelled the order, uses the shared library, and adds nothing extra. Repeat cancellation of an already-cancelled order records nothing, matching the PR text and `orders.py`.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (UNVERIFIED) | `orders.py:2`, `orders.py:16` | The library is not provided. The call `record("order.cancelled", order_id=..., actor=...)` has an assumed event name, keyword names and signature. The import is also module-level, so a missing module or a different export name raises at import. If the real signature differs (for example a required positional argument, other field names, or a context object), every cancel raises `TypeError` or `ImportError`. Because the audit write runs before the status change, no order can then be cancelled at all. | A contract test against the real `company_audit` (or its published stub or type signature) that calls `cancel_order` and asserts the record is accepted. It fails today if the signature differs. |
| 2 | P2 | `orders.py:16-17` | The audit write and `set_status` are not atomic. If `db.set_status` fails after `record` succeeds, the audit says "cancelled" while the order stays open. A retry then writes a second record. Two concurrent requests can both read `open`, both write a record and both set the status, giving duplicate records for one cancellation. This contradicts the claim that cancelling twice records once, which holds only for sequential calls. | A FakeDb whose `set_status` raises: assert what the audit state is after the failure and after a retry. Also a concurrency test with a db whose `get_order` returns `open` to two callers, asserting exactly one record. |
| 3 | P3 | `tests/test_orders.py:11-14` | `sys.modules["company_audit"]` is replaced at import time and never restored. Any other test module in the same process that imports `company_audit` gets the fake, which can hide real-library problems or break other tests. | Run the suite with another test that imports the real module after this file, and assert it gets the real one. Or patch with `unittest.mock.patch.dict` inside `setUpModule` and `tearDownModule`. |
| 4 | P3 | `handlers.py:7` | The PR says `handlers.cancel` is the only caller of `cancel_order`, but the repository outside the provided files was not given. Making `actor` required means any other caller (job, admin script) breaks with `TypeError`. | A repository-wide search for `cancel_order(` in CI, or a test importing every caller. |

**Not a finding:** Failing closed on an audit write error is an intended design. It is stated in the docstring and tested. It does couple cancellations to audit availability. The owner should confirm that is acceptable, but it is not a defect in the code.

## FILES NEEDED BUT NOT PROVIDED
- `company_audit` module source or signature (blocks finding 1)
- Remaining repository files and other callers of `cancel_order` (finding 4)
- Commit trailers for authorship, and CI check results

## Close-out
This is not written yet. The reviewer does not adjudicate its own findings. Once the author adjudicates, the following should be added:
- Adjudication table
- Verification after fixes
- Merge recommendation

Provisional recommendation: **merge after fixes**. Finding 1 must be resolved by checking the real library signature, and finding 2 needs a written decision (fix, or defer with a tracking issue).

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "unverified",
      "location": "orders.py:2, orders.py:16",
      "scenario": "company_audit is not provided and tests stub it. If the real record() signature, event name, or kwargs differ, or the import fails, every cancel raises before set_status and no order can be cancelled.",
      "fix": "Check the call against the real library, add a contract test against the real signature or stub, and keep the call only once confirmed."
    },
    {
      "severity": "P2",
      "evidence_level": "verified in diff",
      "location": "orders.py:16-17",
      "scenario": "Audit write and set_status are not atomic. If set_status fails after the record is written, the audit says cancelled while the order is open, and a retry duplicates the record. Concurrent cancels can both pass the status check and write two records.",
      "fix": "Make the status change and audit record atomic or idempotent (for example a conditional update keyed on order_id and the open status, with a dedupe key on the record), and add failure and concurrency tests."
    },
    {
      "severity": "P3",
      "evidence_level": "verified in diff",
      "location": "tests/test_orders.py:11-14",
      "scenario": "The test replaces sys.modules['company_audit'] globally at import and never restores it, so other tests in the same process get the fake.",
      "fix": "Use mock.patch.dict(sys.modules, ...) in setUpModule and restore it in tearDownModule."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified",
      "location": "handlers.py:7",
      "scenario": "Making actor required breaks any other caller of cancel_order. The claim that handlers.cancel is the only caller cannot be checked from the provided files.",
      "fix": "Search the whole repository for other callers and update or confirm them."
    }
  ]
}
```