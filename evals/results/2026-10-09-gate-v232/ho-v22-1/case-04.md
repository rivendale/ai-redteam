# Redteam report: Pedalo download handlers

**No-tools review.** I could not run code or tests here, so anything I could only trace by reading is marked that way. This is also not an independent seat: no fresh subagent was available. Before production, re-run the tests and the mutations listed below in a real session.

**VERDICT: SHIP WITH FIXES.** The folder-containment check is correct for every hostile name I traced. What remains is two gaps in the test suite (the dropped-separator mutation and symlink escape) and one open question: whether anything limits a rider to their own receipts. The answer to that question could change the verdict.

**CONFIDENCE: medium.** Three things limit it:
- I could not run anything, so the "2 tests pass" claim and the mutation results are unverified.
- The web layer that calls these functions was not supplied.
- I don't know how receipt files are named or who may fetch them.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | – |
| context.md | seen | – |
| downloads.py | seen | – |
| test_downloads.py | seen | – |
| Route/handler wiring (HTTP layer, authentication, error-to-status mapping) | not supplied | **Yes.** It decides whether receipts are scoped to the asking rider and what a missing file returns. |
| Receipt naming scheme and folder layout | not supplied | **Yes.** It decides whether names can be guessed. |
| Test run output | not supplied, and I couldn't run tests | Medium. The context asserts the tests pass. |

**COVERAGE**
- **Checked:**
  - `downloads.py`: `_inside`, `receipt`, `manual`, `station_map`
  - `test_downloads.py`: `setUp`, both tests
  - The claims "2 tests pass" and "refusing any name that resolves outside that folder"
- **Not checked:**
  - The routing/auth layer (not supplied)
  - Runtime behaviour (no tools)
  - The real contents and permissions of `/srv/pedalo/docs`

**SEATS AND GATE**
- Reviewers: same-context self-review only. There was no subagent and no cross-vendor seat.
- Gate: passed. The work is code with no personal data in it. Receipts at runtime are personal data, which feeds the needs-validation item S1.

## Hostile inputs traced through `_inside`

All of these fail safe:

| Input | What happens | Result |
|---|---|---|
| `../secret.txt` | resolves outside the folder | ValueError |
| `/etc/passwd` | `join` discards `base` | ValueError |
| `""` | `real == base`, so no `base+sep` prefix | ValueError |
| `.` | same as `""` | ValueError |
| `../manuals/x` from receipts | lands in a sibling folder | ValueError |
| A symlink inside the folder pointing outside | `realpath` resolves the link | ValueError |
| `receipts-old/...`-style sibling-prefix trick | defeated by `base + os.sep` at `downloads.py:12` | refused |
| A name containing a NUL byte | `realpath`/`lstat` raises | ValueError |

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED | B | `test_downloads.py:21-24`; `downloads.py:12` | The traversal test only uses `../secret.txt`. It would not catch the most likely regression: someone "simplifying" the check to `startswith(base)`. | A future edit drops `+ os.sep`. Then `_inside("maps", "../maps-private/x")` passes when a `maps-private` folder exists. The suite stays green. | Add a sibling folder (e.g. `receipts-old/b.txt`) in `setUp`. Assert `receipt("../receipts-old/b.txt")` raises ValueError. **Reproduction:** mutate line 12 to `startswith(base)` in a scratch copy. The current suite passes; the new test should fail. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED | B | `test_downloads.py` (no symlink or absolute-path case) | The two properties the docstring promises ("resolves outside") have no tests: symlink escape and absolute names. | A refactor replaces `realpath` with `normpath`. A symlink planted in `manuals/` then serves `secret.txt`. No test goes red. | Add `os.symlink(secret, tmp/manuals/link)` and assert ValueError. Add `manual("/etc/passwd")` and assert ValueError. **Reproduction:** swap `realpath` for `normpath` in a scratch copy and confirm the new symlink test fails. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED | B | `downloads.py:19-33` | A missing file raises FileNotFoundError, and a folder name raises IsADirectoryError. Neither becomes a "not found" outcome. Traversal raises ValueError, a different exception. | If the unseen route layer doesn't map these, a bad name returns a 500, possibly with a traceback that shows `/srv/pedalo/docs/...`. A caller can also tell "exists outside" apart from "missing inside". | Catch `(ValueError, OSError)` in the route and return a uniform 404. **Reproduction:** `receipt("nope.pdf")` raises FileNotFoundError, where a 404-equivalent is expected. | a✓ b✓ c✗ d✓ |

## NEEDS VALIDATION

- **S1. Receipt ownership.** `receipt(name)` has no idea who is asking. The docstring example `2026-09-r1.pdf` looks sequential.
  - **Risk:** if the route passes the request name straight through, any rider can enumerate other riders' receipts. That is personal data, so it would be at least High and probably Critical.
  - **What settles it:** whether the route layer authenticates the rider, and whether it restricts names to that rider's receipts. Or whether names are unguessable per-rider tokens.
  - **Note:** the request didn't ask for this. It is still the question most likely to change the verdict.
- **S2. "Handlers" means functions, not routes.** The work adds plain functions. It doesn't show them registered as site endpoints.
  - **What settles it:** whether existing code wires them in, or whether wiring is still to do. If nobody wires them, the request is unmet.
- **S3. Symlink race between check and `open`.** Someone with write access to the docs folders could swap a path for a symlink after `realpath` runs.
  - **What settles it:** whether anything other than deploy tooling can write to `receipts/`, `manuals/` or `maps/`. If nothing can, this is moot.
- **S4. Whole-file read.** `f.read()` loads the whole file into memory.
  - **What settles it:** the largest file sizes, especially for maps and manuals, and the expected number of concurrent downloads.

## REFUTED

- **R1. "The prefix check can be bypassed by a sibling folder with a shared prefix."** The `base + os.sep` at `downloads.py:12` prevents it.
- **R2. "An absolute name escapes the folder."** `os.path.join` returns the absolute path unchanged, `realpath` resolves it, and it fails the prefix check.
- **R3. "The traversal test is vacuous."** If `_inside` stopped refusing, `open(tmp/receipts/../secret.txt)` would succeed. No ValueError would be raised and the test would fail. By that trace the test can go red. I could not run it.

## WHAT HOLDS UP

- `_inside` uses `realpath` on both sides plus a separator-terminated prefix check. That is the right construction.
- All three handlers route through it. There is no handler that skips the check.
- The tests prove normal reads work and that `../` is refused by all three handlers.

## UNVERIFIED CLAIMS

- **"2 tests in test_downloads.py pass."** Confirm with `python -m unittest test_downloads -v`.
- **The traversal test fails when the check is removed.** In a scratch copy, make `_inside` return `real` unconditionally, run the tests, and confirm one goes red.

## QUESTIONS FOR THE AUTHOR

1. Who can call `receipt()`, and does anything restrict a rider to their own receipts?
2. Where are these functions registered as routes, and how do exceptions map to HTTP statuses?

## DECISION-MAKER SUMMARY

The path-traversal protection is sound and applied to all three downloads. Add the two missing tests and a uniform not-found response before shipping. Do not go live until someone confirms that riders can only fetch their own receipts. If they can't, any rider could download other riders' receipts.

## OWNER SUMMARY

The new download feature correctly stops people from reaching files outside the three document folders. A few small test and error-handling gaps should be closed first. The one thing that must be checked before launch is whether a rider could download someone else's receipt just by guessing its name.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "downloads.py", "status": "seen", "matters": true},
    {"item": "test_downloads.py", "status": "seen", "matters": true},
    {"item": "route/auth wiring for the handlers", "status": "not_seen", "matters": true},
    {"item": "receipt naming scheme", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code only; receipts are personal data at runtime (see S1)."},
  "coverage": {
    "checked": [
      {"unit": "downloads.py", "kind": "file"},
      {"unit": "downloads.py:_inside", "kind": "function"},
      {"unit": "downloads.py:receipt", "kind": "function"},
      {"unit": "downloads.py:manual", "kind": "function"},
      {"unit": "downloads.py:station_map", "kind": "function"},
      {"unit": "test_downloads.py", "kind": "file"},
      {"unit": "2 tests pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "route/auth layer", "reason": "not supplied"},
      {"unit": "runtime test execution and mutations", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_downloads.py:21-24; downloads.py:12",
     "scenario": "If '+ os.sep' is dropped from the prefix check, '../receipts-old/b.txt' escapes into a sibling folder and the suite stays green.",
     "fix": "Add a sibling-prefix folder in setUp and assert ValueError for '../receipts-old/b.txt'.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy change line 12 to real.startswith(base); current suite passes, new test fails."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_downloads.py",
     "scenario": "Replacing realpath with normpath lets a symlink in manuals/ serve secret.txt with no test failing.",
     "fix": "Add symlink-escape and absolute-path tests asserting ValueError.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Swap realpath for normpath in a scratch copy; the new symlink test should go red."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py:19-33",
     "scenario": "receipt('nope.pdf') raises FileNotFoundError; unmapped by the route it becomes a 500 that may leak the server path and distinguishes refused from missing.",
     "fix": "Catch ValueError and OSError at the route and return a uniform 404.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Call receipt('nope.pdf'); observe FileNotFoundError, expect a not-found outcome."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "downloads.py:18-21",
     "suspicion": "Any rider may fetch any other rider's receipt by guessing a sequential name.",
     "unresolved_fact": "Whether the route layer authenticates the rider and restricts receipt names to their own, or names are unguessable."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "downloads.py",
     "suspicion": "Functions are not registered as site handlers, so the request may be only partly met.",
     "unresolved_fact": "Whether existing routing code wires these functions in."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "downloads.py:9-13",
     "suspicion": "Symlink swap between realpath and open.",
     "unresolved_fact": "Whether anything other than deploy tooling can write to the docs subfolders."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "downloads.py:20,26,32",
     "suspicion": "Whole-file reads may exhaust memory under concurrent large downloads.",
     "unresolved_fact": "Maximum file size and expected download concurrency."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Sibling-prefix folder bypasses the check.", "evidence": "base + os.sep at downloads.py:12."},
    {"id": "R2", "candidate": "Absolute name escapes the folder.", "evidence": "join returns the absolute path; realpath plus prefix check refuses it."},
    {"id": "R3", "candidate": "Traversal test can never fail.", "evidence": "Without the check, open succeeds and no ValueError is raised, so the test would fail (traced, not run)."}
  ]
}
```