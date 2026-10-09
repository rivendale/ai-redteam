# Redteam report: Pedalo download handlers

> **Review conditions:** I had no tools, so I could not run the code or the tests and could not use a subagent. Every result below comes from reading and tracing the code by hand. The work was not written in this conversation, so the risk of me defending my own work does not apply. Anything that depends on running the code is marked as not executed.

**VERDICT: SHIP.** The path check confines every handler to its own folder, and I found no Critical, High or Medium defect in the supplied code. One Low test gap should be fixed, and one open question (receipt ownership) could change this verdict.

**CONFIDENCE: medium.** It is limited by three things:
- I had no tools, so nothing was executed.
- The web routing layer was not supplied.
- The claim that the 2 tests pass is taken on assertion.

## Inputs ledger

**Seen:**
- `request.md`
- `context.md`
- `downloads.py`
- `test_downloads.py`

**Not seen, and whether the gap matters:**
- **The HTTP routing and authentication layer** that calls these handlers. **This matters.** It decides whether one rider can fetch another rider's receipt, and how exceptions reach the client.
- **The actual docs directory layout and permissions.** This matters a little, for symlink and TOCTOU questions only.
- **The test run output.** It does not matter much. I traced both tests and they should pass.

## Coverage

**Scope:** the whole work, meaning both files.

**Checked:**
- `downloads.py`, including `_inside`, `receipt`, `manual`, `station_map` and the `DOCS` config line
- `test_downloads.py`, including `setUp` and both tests
- `request.md` and `context.md`

**Not checked:**
- The routing and authentication layer (not supplied)
- The deployed `PEDALO_DOCS` value and the directory tree (not supplied)

## Seats and gate

- **Reviewers:** a single local review. No subagent was available, because this session has no tools.
- **Sensitivity gate:** no sensitive data appears in the work itself. Receipts are personal data at runtime, which is relevant to question S1 below. No cross-vendor seats were requested.

## Pass 1: Reconstruct

The work adds three handlers. Each joins a caller-supplied name onto `DOCS/<folder>`, resolves the result with `realpath`, refuses anything that does not start with `base + os.sep`, and then returns the file's bytes.

For this to be correct, three things must hold:
- `realpath` must neutralise `..`, absolute paths and symlinks.
- The separator suffix must stop sibling-prefix escapes, such as `receipts` against a folder named `receipts_old`.
- Something upstream must decide who may request which name.

**Tracks:** B (code), with a light pass of A on requirement fit.

**Trust boundaries:**
- **Principal:** any rider, or any anonymous client if the route is public.
- **Input they control:** `name`.
- **Sensitive sink:** `open()` on the server filesystem, where the docs directory sits beside other server files.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED (traced, not executed) | B | `test_downloads.py:21-24` | The traversal test exercises one input, `"../secret.txt"`. It does not guard the two properties that make `_inside` safe: the `+ os.sep` suffix (`downloads.py:11`) and `realpath` symlink resolution (`downloads.py:9-10`). | A later edit drops `+ os.sep`, or swaps `realpath` for `normpath`. Both tests stay green. A name like `../receipts_old/x.pdf`, or a symlink inside `maps/`, then escapes, and CI does not notice. | **Fix:** add three cases: a sibling folder `receipts_old/x` reached via `../receipts_old/x`; an absolute path; and a symlink in `maps/` pointing at `secret.txt`. Each must raise `ValueError`.<br><br>**Reproduction (do this in a scratch copy only):** change line 11 to `if not real.startswith(base):` and run `python -m unittest test_downloads`. Expected: a failure. Traced result: both tests still pass, because `tmp/secret.txt` does not start with `tmp/receipts`. | a yes, b yes, c no, d no |

## Needs validation (no severity)

**S1. Receipt ownership** (`downloads.py:16-19`)
- `receipt(name)` returns any receipt by file name. There is no rider identity anywhere in the signature.
- The example name, `2026-09-r1.pdf`, looks guessable and enumerable.
- If the route does not check that the receipt belongs to the requesting rider, any rider can read every other rider's receipt. That would be High or Critical (personal data).
- **The fact that settles it:** does the routing layer bind `name` to the authenticated rider and enforce ownership before calling `receipt()`?

**S2. Exception handling at the boundary**
- A missing file raises `FileNotFoundError`. A name that resolves to a directory raises `IsADirectoryError`. A refused name raises `ValueError`. A name containing a NUL byte raises `ValueError` from `open` or `realpath`.
- None of these is caught here.
- **The fact that settles it:** does the web layer turn these into a 404 or 400 without leaking the stack trace or the absolute path?

**S3. Check-then-open race** (`downloads.py:9-13` then `18`)
- A symlink could be swapped between the `realpath` check and the `open()`.
- This is exploitable only by someone who can already write inside `docs/`.
- **The fact that settles it:** can any web-facing process or upload feature write into `docs/<folder>`?

## Refuted

| ID | Candidate | Evidence that refutes it |
|---|---|---|
| C1 | `../` traversal escapes the folder | `realpath` collapses `..` before the prefix check, so `../secret.txt` resolves outside `base` and is refused. |
| C2 | An absolute name escapes | `os.path.join(base, "/etc/passwd")` returns `/etc/passwd`, which fails the prefix check. |
| C3 | Sibling-prefix escape | The check is `base + os.sep`, so `.../receipts_old/x` does not match `.../receipts/`. |
| C4 | Cross-folder reads, e.g. a receipt name reaching manuals | `../manuals/a.txt` resolves outside `DOCS/receipts` and is refused. |
| C5 | Empty name or `"."` returns the folder itself | `real == base` fails the `startswith(base + os.sep)` check, so it raises `ValueError`. |
| C6 | A symlink inside a folder pointing out | `realpath` resolves it before the check, so it is refused. |
| C7 | The tests set `DOCS` too late | `_inside` reads the module global `DOCS` at call time, so `downloads.DOCS = self.tmp` takes effect. |

## What holds up

- `_inside` is the correct pattern: resolve both the base and the target, then compare with a separator. Every handler uses it, and no route reaches `open()` without the check.
- The scope matches the request. There are exactly three handlers with the requested folders, and nothing extra.

## Unverified claims

- **"2 tests in test_downloads.py pass".** I traced both and expect them to pass, but I did not run them. Confirm by running `python -m unittest test_downloads` in a scratch copy.

## Questions for the author

1. Where is receipt ownership enforced, and what stops rider A from requesting rider B's receipt? (This is S1 and could change the verdict.)
2. How does the route map these exceptions to HTTP responses? (This is S2.)

## Decision-maker summary

The path-confinement logic is sound and I could not break it. Ship it, after adding the regression tests in F1. Before production, confirm that the receipt route checks ownership. If it does not, any rider can download other riders' receipts.

## Owner summary

The new download code correctly stops people from reaching files outside the three allowed folders. The tests should cover a few more tricky file names, so that a future change cannot quietly weaken that protection. Before launch, someone should confirm that riders can only download their own receipts.

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
    {"item": "HTTP routing and auth layer calling the handlers", "status": "not_seen", "matters": true},
    {"item": "deployed docs directory layout and permissions", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal data in the work itself; receipts are personal data at runtime (see S1)."},
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
      {"unit": "routing/auth layer", "reason": "not_supplied"},
      {"unit": "test execution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_downloads.py:21-24",
     "scenario": "A later edit drops '+ os.sep' at downloads.py:11 or replaces realpath with normpath; both tests stay green and a sibling-prefix or symlink escape ships unnoticed.",
     "fix": "Add tests for '../receipts_old/x' with that sibling folder present, an absolute path, and a symlink inside maps/ pointing to secret.txt; each must raise ValueError.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy, change downloads.py:11 to 'if not real.startswith(base):' and run 'python -m unittest test_downloads'; expected a failure, traced result is both tests pass (not executed: no tools)."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "downloads.py:16-19",
     "suspicion": "receipt(name) has no rider identity; if the route does not enforce ownership, any rider can read others' receipts by guessable name.",
     "unresolved_fact": "Whether the routing layer binds the name to the authenticated rider and checks ownership before calling receipt()."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "downloads.py:18,24,30",
     "suspicion": "FileNotFoundError, IsADirectoryError and ValueError propagate uncaught and may leak paths or stack traces.",
     "unresolved_fact": "How the web layer maps these exceptions to HTTP responses."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "downloads.py:9-13,18",
     "suspicion": "Check-then-open race allows a symlink swap between realpath and open.",
     "unresolved_fact": "Whether any web-facing process can write inside docs/<folder>."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "'../' traversal escapes the folder.", "evidence": "realpath collapses '..' before the prefix check at downloads.py:9-11."},
    {"id": "C2", "candidate": "An absolute name escapes.", "evidence": "os.path.join(base, '/etc/passwd') yields '/etc/passwd', which fails the startswith check."},
    {"id": "C3", "candidate": "Sibling-prefix escape such as receipts_old.", "evidence": "The check appends os.sep to base at downloads.py:11."},
    {"id": "C4", "candidate": "Cross-folder read, e.g. a receipt name reaching manuals.", "evidence": "'../manuals/a.txt' resolves outside DOCS/receipts and is refused."},
    {"id": "C5", "candidate": "Empty name or '.' returns the folder itself.", "evidence": "real == base fails startswith(base + os.sep), raising ValueError."},
    {"id": "C6", "candidate": "A symlink inside a folder escapes.", "evidence": "realpath resolves symlinks before the comparison."},
    {"id": "C7", "candidate": "Tests set DOCS too late to take effect.", "evidence": "_inside reads the module global DOCS at call time."}
  ]
}
```