# Redteam review: `downloads.py` and `test_downloads.py`

**VERDICT: SHIP.** The containment check holds against every hostile name I traced, the same check guards all three handlers, and nothing I could confirm is above Low. One open question about who may download which receipt should be answered before release.

**CONFIDENCE: medium.**
- I had no tools, so I ran nothing. Every behaviour claim below comes from reading the source against documented Python semantics.
- No web or routing layer was supplied, so I can't see how names arrive or who is allowed to call these functions.
- This was a single reviewer with no fresh-instance seat. The work wasn't written in this conversation, so the anchoring risk is low.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, `downloads.py`, `test_downloads.py`.
- **Not seen:**
  - The route or web layer that calls these handlers. **Matters** for whether receipts are checked against the requesting rider, and for how errors are turned into responses.
  - The deployment layout of `/srv/pedalo/docs`, including who can write into it. Matters a little, only for the symlink-swap question (S3).
  - Test run output. "2 tests pass" is taken on assertion.

**COVERAGE**
- **Scope:** the whole work, meaning both files.
- **Checked:**
  - `downloads.py`: `_inside`, `receipt`, `manual`, `station_map`, and the `DOCS` setting.
  - `test_downloads.py`: `setUp` and both tests.
  - request.md and context.md.
  - The request-fit claim: three handlers, a name from the request, and a file from its folder under docs.
- **Not checked:** the route layer (not supplied); runtime behaviour (no tools).

**SEATS AND GATE:** Only a local same-session review ran. No cross-vendor seat was requested, and none was possible without tools. The sensitivity gate passed: the code contains no personal data. Receipts as a data category are discussed in S1.

## Trust map (Track B)

- **Entry point:** a name chosen by the rider (lower trust).
- **Sensitive action:** reading a file from the server's filesystem.
- **Control:** `_inside`, which runs on all three paths. No handler opens a file without it.

## Hostile names traced through `_inside`

| Name | What happens | Result |
|---|---|---|
| `../secret.txt` | resolves to `DOCS/secret.txt` | refused |
| `/etc/passwd` | `join` drops the base, the path doesn't start with base | refused |
| `../receipts-old/x` | the `+ os.sep` stops the prefix match | refused |
| `""` or `.` | resolves to base itself, which fails the `base + sep` check | refused |
| A symlink inside the folder pointing outside | `realpath` follows it first | refused |
| `sub/../a.pdf` | stays inside the folder | allowed, correctly |
| A name with an embedded NUL | `realpath`/`lstat` raise `ValueError` | refused |

Two further points:
- `DOCS` is read when the function is called, not when the module loads, so the test's override takes effect.
- Even if the `DOCS` folder itself is a symlink, both sides are resolved before comparing, so the check still works.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED (read from the test file) | B | `test_downloads.py:22-25` | The traversal test tries only `../secret.txt`. There is no absolute path, no sibling folder sharing a prefix, and no symlink case. | Someone later "simplifies" line 12 to `real.startswith(base)`. That breaks the guard against sibling folders like `receipts-old`, and both tests still pass. | Add `"/etc/passwd"`, `"../receipts-x/f"` (after creating `receipts-x/f`) and a symlink to `secret.txt` inside each folder. **Repro:** in a scratch copy, delete `+ os.sep` on line 12 and run the tests. Expected: red. Predicted: green. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED (read) | B | `test_downloads.py:14` | `setUp` replaces `downloads.DOCS` and never puts it back. Temporary folders are never deleted. | Any later test in the same process that relies on the real `DOCS` points at a deleted or stale temporary folder. Temporary folders pile up on CI. | Use `unittest.mock.patch.object(downloads, "DOCS", tmp)` with `addCleanup`, and `addCleanup(shutil.rmtree, tmp)`. **Repro:** after the suite runs, `downloads.DOCS` is still the temporary path. | a✓ b✓ c✗ d✗ |

There are no High or Critical findings, so there were none to put through confirm-or-refute or a sibling search.

## NEEDS VALIDATION

- **S1. Receipt ownership.** `receipt(name)` takes no rider identity, so it cannot check that the requesting rider owns the receipt. The example name `2026-09-r1.pdf` looks sequential and guessable.
  - *Fact that settles it:* whether the route layer checks the logged-in rider against the receipt before calling `receipt()`.
  - If it doesn't, any rider can download another rider's receipt. That is personal and financial data, so this would be **High**.
- **S2. Error handling.** A missing file raises `FileNotFoundError`, a folder name such as `subdir` raises `IsADirectoryError`, and a refused name raises `ValueError`. None of these is caught here.
  - *Fact that settles it:* whether the route layer maps these to 404/400. If it doesn't, they surface as 500s, and possibly as stack traces showing server paths.
- **S3. Check-then-open race.** A symlink could be swapped in between `realpath` and `open`.
  - *Fact that settles it:* whether anyone untrusted can write into `docs/*`. If only deploys write there, this is not exploitable.

## REFUTED

- **Prefix bypass** (for example a `receipts-old` sibling). Refuted: line 12 compares against `base + os.sep`.
- **Absolute path bypass.** Refuted: the joined absolute path is resolved, and it fails the prefix check.
- **Symlink escape.** Refuted: `realpath` resolves the target before the comparison.
- **"The traversal test can't fail."** Refuted by tracing: without `_inside`'s check, `open(tmp/secret.txt)` succeeds, so `assertRaises(ValueError)` fails. Confirming this by running it remains UNVERIFIED.

## Assessment

**WHAT HOLDS UP**
- One shared, correct containment function runs on all three handlers.
- The design resolves paths before comparing them, which is the right order.
- The code does exactly what was asked, with no extra features.
- The existing traversal test does guard the basic `../` case.

**UNVERIFIED CLAIMS**
- "2 tests pass." To confirm, run `python -m unittest test_downloads` in a scratch copy.
- That the traversal test goes red under mutation (see F1's repro).

**QUESTIONS FOR THE AUTHOR**
1. Where is receipt ownership enforced?
2. How are `ValueError`, `FileNotFoundError` and `IsADirectoryError` mapped to HTTP responses?

**DECISION-MAKER SUMMARY:** The path-traversal protection is sound on all three handlers, and the only confirmed issues are Low test gaps. Before release, confirm that the receipt route checks the requesting rider owns the receipt. If it doesn't, riders can read each other's receipts.

**OWNER SUMMARY:** The new download code safely stops people from reaching files outside the three allowed folders. The tests could cover a few more tricky cases, but nothing found blocks release. One thing to check first: make sure a rider can only download their own receipts, not anyone else's.

The block below follows schema 2.3 and includes the fields the output note asked for. I could not run `tools/validate_findings.py` against it.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "downloads.py", "status": "seen", "matters": true},
    {"item": "test_downloads.py", "status": "seen", "matters": true},
    {"item": "route/web layer calling the handlers", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code only; receipts as a data category are covered in S1."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "downloads.py", "kind": "file"},
      {"unit": "downloads.py:_inside", "kind": "function"},
      {"unit": "downloads.py:receipt", "kind": "function"},
      {"unit": "downloads.py:manual", "kind": "function"},
      {"unit": "downloads.py:station_map", "kind": "function"},
      {"unit": "test_downloads.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "route/web layer", "reason": "not_supplied"},
      {"unit": "runtime execution of tests", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_downloads.py:22-25",
     "scenario": "If line 12 regresses to real.startswith(base) without os.sep, a sibling-prefix folder becomes reachable and both tests still pass, because only '../secret.txt' is tried.",
     "fix": "Add absolute-path, sibling-prefix ('../receipts-x/f') and symlink-to-outside cases for each handler.",
     "reproduction": "In a scratch copy, remove '+ os.sep' from downloads.py:12 and run python -m unittest test_downloads; expected red, predicted green.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_downloads.py:14",
     "scenario": "setUp overwrites downloads.DOCS and never restores it or deletes the temp dir; later tests in the same process see a stale path, and temp dirs accumulate.",
     "fix": "Use unittest.mock.patch.object with addCleanup, and addCleanup(shutil.rmtree, tmp).",
     "reproduction": "Run the suite, then print downloads.DOCS in the same process; expected the original value, observed the temp path.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "downloads.py:18-21",
     "suspicion": "receipt(name) takes no rider identity, so it cannot enforce ownership; names look sequential and guessable.",
     "unresolved_fact": "Whether the route layer checks the requesting rider owns the receipt before calling receipt()."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "downloads.py:18-33",
     "suspicion": "FileNotFoundError, IsADirectoryError and ValueError propagate uncaught and may surface as 500s with server paths.",
     "unresolved_fact": "How the route layer maps these exceptions to HTTP responses."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "downloads.py:10-14",
     "suspicion": "A symlink swapped between realpath and open could escape the folder.",
     "unresolved_fact": "Whether any untrusted principal can write into the docs subfolders."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Sibling-prefix bypass such as receipts-old.", "evidence": "downloads.py:12 compares against base + os.sep."},
    {"id": "C2", "candidate": "Absolute-path bypass.", "evidence": "The joined absolute path is resolved and fails the prefix check against base + os.sep."},
    {"id": "C3", "candidate": "Symlink escape.", "evidence": "os.path.realpath resolves the link target before the comparison at line 12."},
    {"id": "C4", "candidate": "The traversal test can never fail.", "evidence": "Without the check, open() on tmp/secret.txt succeeds, so assertRaises(ValueError) fails."}
  ]
}
```