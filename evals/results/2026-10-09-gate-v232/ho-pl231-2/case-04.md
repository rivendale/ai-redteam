VERDICT: **SHIP WITH FIXES.** The path containment check holds against every traversal shape I traced, but the tests only exercise one of those shapes, and whether receipts are restricted to their owner is unresolved.
CONFIDENCE IN VERDICT: **medium.** I could not run anything in this session, and the routing and auth layer that calls these functions was not supplied. The receipt-ownership question could raise this to REWORK.

## Pass 1: Reconstruct
The work adds three functions, `receipt`, `manual` and `station_map`. Each takes a caller-supplied name and returns the bytes of `DOCS/<folder>/<name>`. `_inside` refuses any name whose resolved real path is not strictly under the resolved folder. The tests claim normal names work and that `../secret.txt` is refused by all three handlers.

Load-bearing assumptions:
1. `realpath` plus the `base + os.sep` prefix test is enough to contain names.
2. Something upstream handles HTTP: the route, content type, mapping exceptions to 404, and authentication.
3. Receipts are either not private, or ownership is enforced before `receipt(name)` is called.
4. Nobody less trusted can write into the docs folders. The check-then-open sequence is not atomic.

## Pass 2: Attack (Track B, with a Track R note on receipts)

I traced these hostile names through `_inside` (`downloads.py:8-14`), with `base = realpath(DOCS/receipts)`:

| Input | Resolved `real` | Result |
|---|---|---|
| `../secret.txt` | `DOCS/secret.txt` | refused |
| `/etc/passwd` | `join` discards `base`, giving `/etc/passwd` | refused |
| `../receipts_old/x` (sibling folder sharing the prefix) | `DOCS/receipts_old/x` | refused, because of the `+ os.sep` |
| `""` or `.` | equals `base` | refused (needs the trailing sep) |
| a symlink inside `receipts/` pointing outside | resolved by `realpath` | refused |
| `a\x00b` | raises `ValueError` from the OS layer | refused, same exception type |
| `sub/` (a directory inside the folder) | inside | `IsADirectoryError` at `open` (an error, not a leak) |

`os.environ.get`, `os.path.realpath`, `os.path.join` and `os.sep` exist and behave as the code assumes.

## Pass 3: Self-check
- No High or Critical finding was confirmed. The strongest candidate, the receipt access question, depends on code I was not given, so it is recorded under NEEDS VALIDATION and does not set the verdict.
- The work contains no text addressed to the reviewer.
- What I might still be missing: the HTTP wiring. That layer may URL-decode twice, put the name into a `Content-Disposition` header, or log full paths. None of it was supplied.

---

COVERAGE
- `downloads.py`: checked. I traced every line and the hostile inputs above.
- `test_downloads.py`: checked. I read it and traced mutations by hand; I did not run it (no tools).
- `request.md`, `context.md`: checked.
- Route, auth and HTTP layer: not checked, because it was not supplied.

FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED (traced) | `test_downloads.py:22-25` | The traversal test only uses `../secret.txt`. Both hardening details in `_inside` can be removed without the test failing. | Someone later simplifies `startswith(base + os.sep)` to `startswith(base)`, or `realpath` to `normpath`/`abspath`. With `normpath`, a symlink in `maps/` pointing to `/srv/pedalo/` is served; with no `os.sep`, `../receipts_old/x` is served. The suite stays green either way. | Add cases for `/etc/passwd` (absolute), `../receipts2/a.txt` (create sibling folder `receipts2`), `""`, and a symlink `receipts/link -> ../secret.txt`. Reproduce in a scratch copy: apply each mutation, run the current suite (still green), add the cases (red), restore. | a Y, b Y, c N, d N |
| 2 | Low | PROBABLE | `downloads.py:17-33` vs the request's "download handlers" | These are file readers, not handlers. They have no route, no content type, and no error contract. Refusal (`ValueError`), missing file (`FileNotFoundError`) and directory (`IsADirectoryError`) all escape as raw exceptions. | If the caller does not catch them, a rider gets a 500 response, and possibly a traceback containing the server path `/srv/pedalo/docs/...`. | Either define the contract (for example, all three map to 404) or show the wiring. Reproduce: `manual("nope.pdf")` raises `FileNotFoundError`. | a Y, b N, c N, d Y |
| 3 | Low | CONFIRMED | `test_downloads.py:8-14` | `setUp` overwrites the module global `downloads.DOCS` and never restores it, and the temp directories are never removed. | Any later test in the same process that relies on the real `DOCS` reads a stale temp directory. Temp directories pile up on CI. | Use `tempfile.TemporaryDirectory` with `addCleanup`, and patch `DOCS` with `unittest.mock.patch.object`. | a Y, b Y, c N, d N |

NEEDS VALIDATION
- **Receipt ownership.** `receipt(name)` has no rider identity, and the example name `2026-09-r1.pdf` looks sequential and guessable. If the route passes the request's name straight through, any rider can download any other rider's receipt, which is personal and payment data. *Settling fact:* does the route check that the logged-in rider owns that receipt before calling `receipt()`? If not, this is Critical.
- **Check-then-open race.** `_inside` resolves the path, then `open` re-resolves it. Someone able to write into a docs folder could swap in a symlink in between. *Settling fact:* can anything less trusted than the server write to `receipts/`, `manuals/` or `maps/`, for example through receipt generation from user input or an upload feature?
- **"2 tests pass".** *Settling fact:* run `python -m unittest test_downloads -v` and show the output.

REFUTED
- **Sibling-prefix bypass** (`../receipts_old/...`): refuted by `base + os.sep` (`downloads.py:12`).
- **Absolute-path name:** `join` returns `/etc/passwd`, which fails the prefix check.
- **Symlink escape at rest:** `realpath` resolves the link before the check.
- **Empty name or `.`:** resolves to `base`, which fails the check because of the trailing separator.
- **NUL byte:** raises `ValueError` and is never served.

WHAT HOLDS UP
The containment logic is correct: it resolves real paths on both sides and compares against `base + os.sep`. All three handlers use the same helper with the right folder (receipts, manuals, maps). The traversal test does go red if the check is removed entirely, because `open` would then return `top secret` without raising.

UNVERIFIED CLAIMS
- "2 tests pass": run the suite.
- The handlers are reachable only through a safe route: show the routing code.
- The production `PEDALO_DOCS` is the intended directory: check the deployed environment.

QUESTIONS FOR THE AUTHOR
1. Where is ownership of a receipt checked before `receipt(name)` is called?
2. Can any process handling rider input write into the docs folders?
3. How does the route turn these exceptions into HTTP responses?

DECISION-MAKER SUMMARY
The path-traversal protection is sound and can ship once the tests are widened to lock it in (finding 1). Before release, confirm that a rider can only fetch their own receipts. If that check does not exist, receipts are exposed to any logged-in user and the verdict becomes REWORK.

OWNER SUMMARY
The new download feature correctly stops people from reaching files outside the intended folders, but its tests only check one kind of attack and should cover a few more. One question needs an answer before launch: whether a rider can download other riders' receipts by guessing file names. If they can, that must be fixed first.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "downloads.py", "status": "seen", "matters": true},
    {"item": "test_downloads.py", "status": "seen", "matters": true},
    {"item": "route/auth layer calling the handlers", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "downloads.py", "kind": "file"},
      {"unit": "downloads._inside", "kind": "function"},
      {"unit": "test_downloads.py", "kind": "file"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "HTTP route and auth wiring", "reason": "not_supplied"},
      {"unit": "test execution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
      "location": "test_downloads.py:22-25",
      "scenario": "Mutating startswith(base + os.sep) to startswith(base), or realpath to normpath, leaves the suite green; a sibling folder ../receipts2/ or a symlink escape would then be served.",
      "fix": "Add traversal cases: absolute path, sibling-prefix folder, empty name, symlink pointing outside.",
      "reproduction": "In a scratch copy apply each mutation, run python -m unittest test_downloads (green), add the cases (red), restore.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
      "location": "downloads.py:17-33",
      "scenario": "ValueError, FileNotFoundError and IsADirectoryError escape the handlers; if uncaught upstream a rider gets a 500, possibly with a traceback exposing /srv/pedalo/docs paths.",
      "fix": "Define an error contract (map all three to 404) or show the route wiring that does.",
      "reproduction": "manual('nope.pdf') raises FileNotFoundError; manual('../x') raises ValueError.",
      "answers": {"a": true, "b": false, "c": false, "d": true}
    },
    {
      "id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "test_downloads.py:8-14",
      "scenario": "setUp overwrites downloads.DOCS and never restores it, and temp dirs are never removed; later tests in the same process read a stale temp dir.",
      "fix": "Use tempfile.TemporaryDirectory with addCleanup, and mock.patch.object(downloads, 'DOCS', ...).",
      "reproduction": "Run the suite, then print downloads.DOCS in the same process: it is a leftover /tmp path.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "NV1", "status": "needs_validation", "location": "downloads.py:17-20 (receipt)",
      "suspicion": "No rider identity reaches receipt(); predictable names like 2026-09-r1.pdf would let any rider fetch another rider's receipt.",
      "unresolved_fact": "Does the route verify the logged-in rider owns the requested receipt before calling receipt()?"
    },
    {
      "id": "NV2", "status": "needs_validation", "location": "downloads.py:10-11 then open()",
      "suspicion": "Check-then-open race: a symlink swapped in after realpath and before open escapes the folder.",
      "unresolved_fact": "Can any lower-trust process write into the receipts, manuals or maps folders?"
    },
    {
      "id": "NV3", "status": "needs_validation", "location": "context.md",
      "suspicion": "The claim that the two tests pass has not been shown.",
      "unresolved_fact": "Output of python -m unittest test_downloads -v."
    }
  ],
  "refuted": [
    {"id": "R1", "candidate": "Sibling-prefix bypass via ../receipts_old/", "evidence": "The check uses base + os.sep (downloads.py:12)."},
    {"id": "R2", "candidate": "Absolute path name such as /etc/passwd", "evidence": "os.path.join returns /etc/passwd, which fails the prefix check."},
    {"id": "R3", "candidate": "Symlink escape at rest", "evidence": "realpath resolves the link before the comparison."},
    {"id": "R4", "candidate": "Empty name or '.' returns the folder", "evidence": "It resolves to base, which lacks the trailing separator, so ValueError is raised."},
    {"id": "R5", "candidate": "NUL byte bypass", "evidence": "The OS layer raises ValueError; nothing is served."}
  ]
}
```