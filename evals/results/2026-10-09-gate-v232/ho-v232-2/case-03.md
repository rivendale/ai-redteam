**Single-reviewer review with no tools.** I did not write this work, so there is no anchoring on authorship. No subagent or cross-vendor seats were available, and nothing was executed. Findings below rest on tracing the exact lines against Python's documented `os.path` semantics.

**VERDICT: REWORK.** Two of the three handlers (`receipt`, `manual`) pass the request's file name straight to `open()` with no containment check, so any caller can read any file the server process can read.

**CONFIDENCE: high** for the findings, which are deterministic and traced line by line. **Medium** overall, for two reasons:
- I had no tools, so nothing was run.
- The route layer that calls these functions was not supplied.

## Inputs ledger

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | yes |
| context.md | seen | yes |
| downloads.py | seen | yes |
| Route/handler code that calls these functions (auth, error mapping) | not supplied | yes: decides receipt ownership checks and how `ValueError` surfaces |
| Tests | not supplied (context confirms none exist) | yes |
| Deployment: `PEDALO_DOCS` value, process user, contents beside docs/ | not supplied | partly: it sets blast radius, not whether the bug exists |

## Coverage

- **Scope:** the whole work (one file).
- **Checked:**
  - downloads.py: module docstring, `DOCS`, `_inside`, `receipt`, `manual`, `station_map`
  - request.md
  - context.md
- **Not checked:**
  - Route handlers and auth: not supplied.
  - Tests: not supplied.
  - Deployment config: not supplied.

## Seats and gate

- **Local reviewer:** ran.
- **Independent subagent / cross-vendor seats:** none available.
- **Sensitivity gate:** the code itself is not sensitive. Receipts are rider personal data, but none was supplied.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | downloads.py:18-19 `receipt` | `os.path.join(DOCS, "receipts", name)` is opened with no containment check. `../` segments escape the folder, and an absolute `name` discards the prefix entirely (documented `os.path.join` behaviour). | A request with `name=../../../etc/passwd`, or `name=/srv/pedalo/<server config>`, returns that file's bytes. Context says docs/ sits beside other server files, so config and secrets are one `../` away. | **Fix:** `open(_inside("receipts", name), "rb")`. **Repro (scratch copy, no network, empty env):** set `PEDALO_DOCS=$tmp/docs`, create `$tmp/docs/receipts/` and `$tmp/docs/secret.txt`, then call `receipt('../secret.txt')` and `receipt('/etc/hostname')`. Expected: `ValueError`. Observed per trace: file contents returned. | y/y/y/y |
| F2 | Critical | CONFIRMED (traced) | B | downloads.py:24-25 `manual` | Same root cause as F1, in the manuals folder. | `name=../../<file>` or an absolute path returns arbitrary server files. | **Fix:** `open(_inside("manuals", name), "rb")`. **Repro:** as F1 with `manuals/`. `manual('../secret.txt')` should raise `ValueError` but returns the contents. | y/y/y/y |
| F3 | Medium | CONFIRMED | B | downloads.py (whole file); context.md "No tests were supplied" | There is no test of the traversal guard. The author wrote `_inside` and applied it to one handler of three, which is exactly the regression a test would catch. | A future handler or edit drops the guard, and nothing goes red. | **Fix:** add a parametrised test over all three handlers with `../x`, an absolute path, `""`, and a symlink pointing outside, each asserting `ValueError`. **Repro:** that test fails today for `receipt` and `manual`. Confirm it goes red by temporarily removing `_inside` from `station_map` in a scratch copy. | y/y/n/n |

### Sibling search (F1, F2)

- **Searched:** every `open()` and `os.path.join` call in downloads.py, and all three handlers.
- **Found:**
  - `receipt` (F1) and `manual` (F2) are unguarded.
  - `station_map` routes through `_inside`.
- The caller layer was not supplied, so siblings there are unchecked.

### Security boundary (F1, F2)

- **Principal:** any client able to call the download endpoints.
- **Input:** the file name from the request.
- **Control that fails:** no containment check exists on these paths.
- **Boundary crossed:** web request into the server filesystem outside docs/.
- **Resource affected:** any file readable by the server process.

## Needs validation

- **S1: receipt ownership.** `receipt` returns any receipt by name, and the example names (`2026-09-r1.pdf`) look guessable. Rider A could fetch rider B's receipt, which is personal data.
  - *Settles it:* whether the route layer checks that the requested receipt belongs to the authenticated rider.
- **S2: `ValueError` handling.** `_inside` raises `ValueError`, and `open()` can raise `FileNotFoundError` or `IsADirectoryError` (e.g. `name="."` is caught by `_inside`, but a subdirectory name is not).
  - *Settles it:* whether the handlers map these to 400/404 rather than a 500 that may expose a traceback with paths.
- **S3: symlink race (TOCTOU).** There is a gap between `realpath` in `_inside` and `open()`, so a symlink swapped in between would bypass the check.
  - *Settles it:* whether any lower-trust principal can write into docs/maps (or receipts/manuals once fixed). If not, this is not exploitable.

## Refuted

- **Prefix collision (`maps` vs `maps2`):** `_inside` compares against `base + os.sep`, so `/srv/pedalo/docs/maps2/x` does not match `/srv/pedalo/docs/maps/`.
- **Absolute or `..` name bypassing `station_map`:** `realpath(join(base, "/etc/passwd"))` is `/etc/passwd`, which fails the prefix check. `..` is resolved before the comparison.
- **Empty name or `"."` in `station_map`:** `real == base` lacks the trailing separator, so it raises `ValueError` rather than opening the directory.
- **Symlink inside maps pointing outside:** `realpath` resolves it, so it is rejected (apart from the race in S3).

## What holds up

- `_inside` is correctly written. It uses `realpath` on both sides, a separator-terminated prefix, and handles absolute names.
- `station_map` uses it correctly.
- Files are opened in binary mode, and handles are closed via `with`.

## Unverified claims

- None asserted by the work. The module docstring correctly states "Names come from the request", which makes F1 and F2 a sibling miss rather than an unknown threat model.
- My trace of `os.path.join`/`realpath` behaviour was not executed. Run the F1 and F2 reproductions in an isolated scratch copy to confirm.

## Questions for the author

1. Does the route layer check that a receipt belongs to the requesting rider (S1)?
2. How are `ValueError` and `OSError` from these functions turned into HTTP responses (S2)?

## Decision-maker summary

Do not deploy: the receipt and manual downloads let anyone read arbitrary server files, including whatever sits beside the docs directory. The fix is two one-line changes to use the existing `_inside` guard, plus a test covering all three handlers. Separately, confirm that receipts are restricted to their owner.

## Owner summary

Two of the three new download features can be tricked into handing out any file on the server, not just the documents they are meant to serve. The protection already exists in the code but was only applied to the station maps, so the repair is small. We should also confirm that riders can only download their own receipts before this goes live.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "downloads.py", "status": "seen", "matters": true},
    {"item": "route/handler layer calling downloads.py", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "deployment config (PEDALO_DOCS, process user)", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-reviewer-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code only; receipts are personal data but none was supplied."},
  "coverage": {
    "checked": [
      {"unit": "downloads.py", "kind": "file"},
      {"unit": "downloads.py:_inside", "kind": "function"},
      {"unit": "downloads.py:receipt", "kind": "function"},
      {"unit": "downloads.py:manual", "kind": "function"},
      {"unit": "downloads.py:station_map", "kind": "function"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "route/handler layer", "reason": "not_supplied"},
      {"unit": "tests", "reason": "not_supplied"},
      {"unit": "deployment config", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py:18-19 (receipt)",
     "scenario": "A request with name '../../../etc/passwd' or an absolute path returns that file, because os.path.join(DOCS, 'receipts', name) is opened with no containment check and an absolute name discards the prefix.",
     "fix": "open(_inside('receipts', name), 'rb').",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "In a scratch copy with no network and an empty env: PEDALO_DOCS=$tmp/docs, create $tmp/docs/receipts/ and $tmp/docs/secret.txt; call receipt('../secret.txt') and receipt('/etc/hostname'); expected ValueError, observed (per trace) file contents returned.",
     "security": true,
     "boundary": {"principal": "any client able to call the receipt download", "input": "the file name from the request",
                  "control": "no containment check (_inside not called)", "crossed": "web request to server filesystem outside docs/receipts",
                  "resource": "any file readable by the server process, including server files beside docs/"},
     "siblings_searched": {"searched": "every open() and os.path.join call and all three handlers in downloads.py",
                           "found": "manual has the same defect (F2); station_map uses _inside"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py:24-25 (manual)",
     "scenario": "A request with name '../../<file>' or an absolute path returns arbitrary server files from the manuals handler.",
     "fix": "open(_inside('manuals', name), 'rb').",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "As F1 with $tmp/docs/manuals/; manual('../secret.txt') should raise ValueError but returns the contents.",
     "security": true,
     "boundary": {"principal": "any client able to call the manual download", "input": "the file name from the request",
                  "control": "no containment check (_inside not called)", "crossed": "web request to server filesystem outside docs/manuals",
                  "resource": "any file readable by the server process"},
     "siblings_searched": {"searched": "every open() and os.path.join call and all three handlers in downloads.py",
                           "found": "receipt has the same defect (F1); station_map uses _inside"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py (whole file); context.md 'No tests were supplied'",
     "scenario": "No test asserts that traversal is refused, so the guard was applied to one handler of three and a future edit can drop it with nothing going red.",
     "fix": "Add a parametrised test over all three handlers with '../x', an absolute path, '', and an outward symlink, each asserting ValueError.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "The proposed test fails today for receipt and manual; confirm it goes red for station_map by removing _inside in a scratch copy."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "downloads.py:17-20 (receipt)",
     "suspicion": "Any rider can fetch another rider's receipt by guessing its name.",
     "unresolved_fact": "Whether the route layer checks receipt ownership against the authenticated rider."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "downloads.py:12 and all open() calls",
     "suspicion": "ValueError/OSError may surface as a 500 with a traceback exposing paths.",
     "unresolved_fact": "How the route layer maps these exceptions to HTTP responses."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "downloads.py:10-14 and 30",
     "suspicion": "A symlink swapped in between realpath and open() bypasses _inside.",
     "unresolved_fact": "Whether any lower-trust principal can write into the docs subfolders."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Prefix collision lets maps2/ pass the maps/ check.", "evidence": "_inside compares against base + os.sep."},
    {"id": "C2", "candidate": "An absolute or '..' name bypasses station_map.", "evidence": "realpath resolves it before the prefix check, which then fails."},
    {"id": "C3", "candidate": "An empty name or '.' opens the maps directory.", "evidence": "real == base lacks the trailing separator, so ValueError is raised."}
  ]
}
```