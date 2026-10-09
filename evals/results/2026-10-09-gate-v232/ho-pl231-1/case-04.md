**VERDICT: SHIP WITH FIXES.** The path containment in `_inside` holds against the common traversal attacks, but the receipt handler has no ownership check, so any rider who can guess a name can download another rider's receipt.

**CONFIDENCE IN VERDICT: medium.** I had no tools, so nothing was run. I could not see the routing layer, so I don't know whether something upstream limits which receipt names a rider can request. The two tests were traced by hand, not executed.

## Pass 1: Reconstruct

The work adds three functions, `receipt`, `manual` and `station_map`. Each takes a caller-supplied file name and returns the bytes of that file from `DOCS/receipts`, `DOCS/manuals` or `DOCS/maps`. Containment is enforced by `_inside`, which resolves both the folder and the requested path with `realpath` and refuses anything not strictly under the folder.

For this to be correct, four things must hold:
- `realpath` and a prefix check on `base + os.sep` are enough to keep every request inside its folder.
- The caller turns exceptions into sensible HTTP responses.
- It is acceptable for anyone who can call a handler to read every file in its folder. This is unstated, and it is load-bearing for receipts.
- Nobody untrusted can write into the docs folders, which would open a symlink-swap race between the check and the open.

## Pass 2: Attack (Track B, with Track R for receipt personal data)

Hostile inputs traced through `_inside` (`downloads.py:8-14`):

| Input | Trace | Result |
|---|---|---|
| `../secret.txt` | resolves to `DOCS/secret.txt`, which is not under `DOCS/receipts/` | refused ✔ |
| `/etc/passwd` | `os.path.join(base, "/etc/passwd")` discards `base`, giving `/etc/passwd` | refused ✔ |
| `../receipts_old/x` (sibling folder whose name starts with the same prefix) | `startswith(base + os.sep)` rejects `.../receipts_old` | refused ✔ |
| A symlink inside the folder pointing outside it | `realpath` follows it to the outside target | refused ✔ |
| `""` or `.` | resolves to `base` itself, which does not start with `base + "/"` | refused (ValueError) ✔ |
| `a\x00b` | `lstat` or `open` raises ValueError for an embedded null byte | refused ✔ |
| `subdir` (a directory inside the folder) | `open` raises IsADirectoryError | uncaught (Finding 3) |
| A missing file | FileNotFoundError | uncaught (Finding 3) |
| `2026-09-r2.pdf` requested by a different rider | no identity check exists | **another rider's receipt is returned** (Finding 1) |

Mutation analysis of the tests (rule 5, done mentally because I had no tools):
- Removing the containment check makes `../secret.txt` open successfully, so `test_traversal_is_refused_by_every_handler` goes red. That test does guard the basic case.
- Changing `base + os.sep` to `base`, or `realpath` to `abspath`, leaves both tests green. Sibling-prefix and symlink escapes are unguarded by tests (Finding 2).

## FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | High | PROBABLE (the missing check is confirmed; exploitability depends on routing I can't see) | `downloads.py:17-20`, `receipt(name)` | The receipt handler takes only a file name. Nothing ties a receipt to the rider asking for it. The docstring example `2026-09-r1.pdf` suggests sequential, guessable names. | Rider A is logged in and calls `receipt('2026-09-r2.pdf')`, `r3`, and so on. They get other riders' receipts, which carry personal and payment data. | Pass the authenticated rider's id and scope the lookup, for example `DOCS/receipts/<rider_id>/<name>`. Alternatively, check ownership against the receipt record before opening. Repro: put `r1.pdf` (owned by A) and `r2.pdf` (owned by B) in `receipts/`, then call the handler as A for `r2.pdf`. It returns B's file. | a Y / b N / c Y / d Y |
| 2 | Medium | CONFIRMED | `test_downloads.py:21-24` | Only one escape vector is tested (`../`). The tests would still pass if the `os.sep` guard or the use of `realpath` were weakened. | A future refactor changes `realpath` to `abspath`. A symlink planted in `maps/` then escapes the folder and CI stays green. | Add tests for an absolute path (`/etc/passwd`), a sibling-prefix folder (`receipts_x/` beside `receipts/`), and a symlink inside the folder pointing to `secret.txt`. Mutate each guard in a scratch copy and confirm the matching test goes red. | a Y / b Y / c N / d N |
| 3 | Low | CONFIRMED | `downloads.py:18,24,30` | Missing files, directories and refused paths raise FileNotFoundError, IsADirectoryError or ValueError. Nothing maps these to 404 or 400. | `receipt('nope.pdf')` causes a 500 error. If debug pages are on, the traceback shows `/srv/pedalo/docs/...`. | Catch the errors in each handler or in the route layer and return 404 for all three cases. Repro: call `manual('nope.pdf')`. | a Y / b Y / c N / d Y |

**Self-check on Finding 1.** The strongest defence is that the request said only "take a file name and return the file", so authorization might live in the route layer. That defence is weak. A route that holds only a file name cannot verify ownership unless it keeps a separate name-to-rider mapping. Nothing in the work mentions one. I kept the finding at High and marked it PROBABLE pending that one fact.

I searched for the same root cause in the other handlers. `manual` and `station_map` serve public content, so no per-rider check is needed there. No siblings found.

The security framing for Finding 1:
- **Principal:** an authenticated rider.
- **Input:** the `name` parameter.
- **Failing control:** there is no ownership check.
- **Boundary crossed:** one rider to another.
- **Resource affected:** other riders' receipt files.

**What I might still be missing:** whether the docs folders can be written by anything untrusted, such as an upload feature or a shared mount. If they can, the gap between `realpath` and `open` becomes a symlink-swap race.

## NEEDS VALIDATION

- **Receipt access from the routing layer.** Does the route restrict which receipt names a rider can request, for example with unguessable per-rider tokens or a lookup against the rider's own records? If yes, Finding 1 drops to Low.
- **Race between check and open (`downloads.py:11-19`).** Can any untrusted process write into `DOCS/*`? If yes, use `os.open(..., O_NOFOLLOW)` relative to a directory file descriptor.
- **Whether the code satisfies the request's "handlers".** Is there a framework or route registration that wires these functions up? The work has only plain functions and no routes.

## REFUTED

- **Absolute path escape:** refuted. `join` discards `base`, and the prefix check then rejects the path.
- **Sibling-prefix escape:** refuted. The check uses `base + os.sep`.
- **Symlink escape:** refuted. `realpath` resolves the link before the check.
- **The tests freezing `DOCS` at import time:** refuted. `_inside` reads the module global `DOCS` at call time, so the override in `setUp` takes effect.
- **Error types revealing whether files exist outside the folder:** refuted. Out-of-folder names fail with ValueError before any open, so the error does not reveal whether the file exists.

## WHAT HOLDS UP

The containment logic in `_inside` is correct for `../`, absolute paths, sibling prefixes, symlinks, empty names and null bytes. The existing traversal test fails if the check is removed. All three handlers share one guard, so there is no copy-paste drift between them.

## UNVERIFIED CLAIMS

- "2 tests in test_downloads.py pass." I could not run them; my hand trace says they would pass. Confirm with `python -m unittest test_downloads`.

## QUESTIONS FOR THE AUTHOR

1. How is a receipt tied to the rider allowed to fetch it?
2. Can anything untrusted write into the docs folders?

## DECISION-MAKER SUMMARY

Manuals and maps are safe to ship. The traversal protection is sound. Hold receipts until downloads are scoped to the logged-in rider, or until the route layer is shown to enforce ownership. Otherwise riders can likely download each other's receipts.

## OWNER SUMMARY

The new download feature correctly stops people from reaching server files outside the documents folder. However, as written, one rider could probably download another rider's receipts by guessing file names, which would expose personal and payment details. Fix that before launch and add a few more tests; the manuals and maps downloads are fine.

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
    {"item": "routing/auth layer", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "downloads.py", "kind": "file"},
      {"unit": "test_downloads.py", "kind": "file"},
      {"unit": "_inside", "kind": "function"},
      {"unit": "tests pass claim", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "route registration and auth layer", "reason": "not_supplied"},
      {"unit": "test execution and mutation runs", "reason": "no_tools"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
      "location": "downloads.py:17-20 receipt(name)",
      "scenario": "Authenticated rider A requests receipt('2026-09-r2.pdf') belonging to rider B and receives B's receipt; there is no ownership check and names look sequential.",
      "fix": "Scope receipts to the authenticated rider (DOCS/receipts/<rider_id>/<name>) or verify ownership before opening.",
      "answers": {"a": true, "b": false, "c": true, "d": true},
      "reproduction": "Place r1.pdf (rider A) and r2.pdf (rider B) in receipts/; call the handler as A for r2.pdf; B's file is returned.",
      "security": true,
      "siblings_searched": {"searched": "manual() and station_map() for per-user data needing ownership checks", "found": "none; both serve public content"},
      "boundary": {"principal": "authenticated rider", "input": "name parameter", "control": "missing ownership check", "crossed": "rider-to-rider", "resource": "other riders' receipt files"}
    },
    {
      "id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
      "location": "test_downloads.py:21-24",
      "scenario": "Changing realpath to abspath or dropping os.sep from the prefix check leaves both tests green, so a symlink or sibling-prefix escape could ship unnoticed.",
      "fix": "Add tests for an absolute path, a sibling-prefix folder and a symlink to secret.txt; confirm each fails under the matching mutation.",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "In a scratch copy, replace os.path.realpath with os.path.abspath in _inside and run the tests: both pass."
    },
    {
      "id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "downloads.py:18,24,30",
      "scenario": "manual('nope.pdf') or receipt('subdir') raises FileNotFoundError or IsADirectoryError, which surfaces as a 500 and may leak paths in debug mode.",
      "fix": "Map FileNotFoundError, IsADirectoryError and ValueError to a 404 response.",
      "answers": {"a": true, "b": true, "c": false, "d": true},
      "reproduction": "Call downloads.manual('nope.pdf'); an uncaught FileNotFoundError is raised."
    },
    {
      "id": "NV1", "status": "needs_validation",
      "location": "routing layer (not supplied)",
      "suspicion": "Ownership of receipts may be enforced upstream.",
      "unresolved_fact": "Does the route restrict receipt names to the requesting rider?"
    },
    {
      "id": "NV2", "status": "needs_validation",
      "location": "downloads.py:11-19",
      "suspicion": "A symlink could be swapped in between the realpath check and open.",
      "unresolved_fact": "Can any untrusted process write into DOCS/*?"
    },
    {
      "id": "NV3", "status": "needs_validation",
      "location": "downloads.py (whole file)",
      "suspicion": "Plain functions may not satisfy the request for site download handlers.",
      "unresolved_fact": "Is there route registration that wires these functions into the rider site?"
    }
  ],
  "refuted": [
    {"id": "R1", "candidate": "Absolute path escape", "evidence": "os.path.join discards base; the resolved path fails the startswith(base + os.sep) check."},
    {"id": "R2", "candidate": "Sibling-prefix escape (receipts_old)", "evidence": "The check compares against base + os.sep, so a sibling folder name does not match."},
    {"id": "R3", "candidate": "Symlink escape", "evidence": "realpath resolves the link before the prefix check."},
    {"id": "R4", "candidate": "DOCS frozen at import breaks the tests", "evidence": "_inside reads the module global DOCS at call time, so the setUp override applies."},
    {"id": "R5", "candidate": "Existence oracle outside the folder", "evidence": "Out-of-folder names raise ValueError before any open attempt."}
  ]
}
```