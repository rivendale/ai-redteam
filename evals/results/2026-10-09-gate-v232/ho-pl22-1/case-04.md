VERDICT: **SHIP WITH FIXES.** The path-traversal guard is correctly built, but the receipts handler will serve any rider's receipt to anyone who supplies its file name, and nothing in the work shows an ownership check anywhere.

CONFIDENCE IN VERDICT: **Medium.** I had no tools, so nothing was run, and the routing layer that calls these functions was not provided. If that layer already enforces receipt ownership, finding 1 drops and this becomes SHIP after the test fixes. If no such check exists, receipts should not ship.

## Pass 1: Reconstruct

The work adds three functions, `receipt`, `manual` and `station_map`. Each takes a name from the request and returns the bytes of `DOCS/<folder>/<name>`. All three go through `_inside`, which resolves the real path and refuses anything that lands outside the folder. Two tests cover the normal path and a `../` escape.

For this to be correct, these assumptions must hold:

- `realpath` followed by a prefix check plus `os.sep` is enough to contain names.
- Any file in each folder may be given to anyone who asks for it. For receipts this assumption is unstated and doubtful.
- Some layer that was not shown turns these functions into HTTP handlers and maps the exceptions to sensible responses.
- Nobody untrusted can write into the docs folders.

## Pass 2: Attack, guard trace

I traced `downloads.py:8-13` against hostile inputs:

| Input | Resolution | Result |
|---|---|---|
| `../secret.txt` | `DOCS/secret.txt` | refused ✔ |
| `/etc/passwd` | `join` discards base → `/etc/passwd` | refused ✔ |
| `../receipts2/x` (sibling prefix) | `DOCS/receipts2/x` | refused, because of `+ os.sep` ✔ |
| symlink in folder → `/etc` | realpath follows it | refused ✔ |
| `""` or `.` | `real == base` | refused ✔ (no directory open) |
| `sub/` (subdirectory) | inside | `IsADirectoryError` (see finding 3) |

The containment logic holds.

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | High (Critical if there is no upstream check) | CONFIRMED: no ownership check in the code. UNVERIFIED: whether the route layer adds one | `downloads.py` `receipt()`, docstring `receipt('2026-09-r1.pdf')` | The only check is that the file sits in the folder. Receipts belong to individual riders and carry personal data, and the example name looks sequential and guessable. | A logged-in or anonymous user requests `2026-09-r2.pdf`, `r3`, … and downloads other riders' receipts (an insecure direct object reference). This is personal-data exposure with regulatory consequences. | Take the authenticated rider's id and confirm the receipt belongs to them, for example with a per-rider subfolder or a database lookup from receipt id to owner. Add a test where rider A requests rider B's receipt and expect refusal. |
| 2 | Medium | PROBABLE (reasoned mutation; nothing was run) | `test_downloads.py` `test_traversal_is_refused_by_every_handler` | The only hostile input tested is `../secret.txt`. The checks that matter most are untested: removing `+ os.sep`, swapping `realpath` for `abspath`/`normpath`, and absolute paths would all still pass. | A later "simplification" brings back a sibling-prefix bypass (`../maps-old/x`) or a symlink escape, and CI stays green. | Add cases for an absolute path, a sibling folder sharing the prefix (`../receiptsX/f`), and a symlink inside a folder pointing at `secret.txt`. Then mutate each guard line in a scratch copy and confirm the matching test goes red. |
| 3 | Medium | UNVERIFIED (no routing shown) | Whole module vs. request "add three download handlers to the rider site" | These are plain functions, not wired handlers. Their errors (`ValueError`, `FileNotFoundError`, `IsADirectoryError`, `PermissionError`) are left for the caller, and no content type or download headers are set. The scope cut is not stated. | The caller lets the exception through, producing a 500. With debug enabled that can leak the absolute server path. A missing receipt and a traversal attempt also become indistinguishable from server faults. | Show the route wiring. Map refusals and missing files to 404 and set `Content-Type`/`Content-Disposition`. Test a missing file and a directory name through the route. |
| 4 | Low | PROBABLE | `_inside` then `open` | There is a check-then-use gap between `realpath` and `open`. | If anyone can write into a docs folder, they can swap a file for a symlink after the check and escape. Low risk if the folders are deploy-only. | Make sure the folders are not writable by the app or by uploaders, or open with `O_NOFOLLOW` / `openat` relative to a directory file descriptor. |
| 5 | Low | CONFIRMED | `test_downloads.py` `setUp` | The temp dir is never removed. `downloads.DOCS` is overwritten globally and never restored. `open(...).write` leaves file handles unclosed. | Test pollution once other test modules import `downloads`, plus leftover temp files. | Use `TemporaryDirectory` plus `addCleanup` and restore `DOCS` with `unittest.mock.patch.object`. |
| 6 | Low | CONFIRMED | `f.read()` in all three handlers | The whole file is read into memory. | Large map images under concurrent load inflate memory use. | Stream the file, or use the framework's send-file helper. |

## WHAT HOLDS UP

- **Containment in `_inside`:** it resolves symlinks, rejects absolute paths, guards sibling prefixes with `+ os.sep`, and refuses the folder itself.
- **Shared guard:** all three handlers route through it, so there is no copy-paste drift.
- **`DOCS` is read at call time**, which makes it testable.
- **The existing traversal test is a valid positive control:** without the guard, `../secret.txt` would open successfully and the test would fail.

## UNVERIFIED CLAIMS

- **"2 tests in test_downloads.py pass":** not run here. Confirm by running `python -m unittest test_downloads -v`.
- **That the routes exist and authenticate riders:** confirm by showing the route code.
- **That the docs folders are not writable by untrusted parties:** confirm by checking deploy permissions.

## QUESTIONS FOR THE AUTHOR

1. Does the route that calls `receipt()` check that the requested receipt belongs to the logged-in rider? If so, where?
2. Are receipt file names guessable or sequential in production?
3. Where are these functions wired into the site, and how are their exceptions turned into responses?

## DECISION-MAKER SUMMARY

Manuals and maps are safe to ship once the tests are hardened. The traversal guard is sound. Do not ship receipts until someone confirms that a rider can only fetch their own receipt; otherwise riders' personal data can be enumerated by guessing file names.

## OWNER SUMMARY

The new download feature correctly stops people from reaching server files outside the documents folders. However, the receipts download appears to let anyone fetch any rider's receipt just by guessing its name, which would expose personal information. That check should be added or confirmed before receipts go live, and the tests should be strengthened so the protection cannot quietly break later.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "downloads.py receipt(); docstring example receipt('2026-09-r1.pdf')",
      "scenario": "No ownership check: any user requests guessable names like 2026-09-r2.pdf and downloads other riders' receipts (personal data). Critical if no upstream route check exists (unverified).",
      "fix": "Pass the authenticated rider id and verify receipt ownership (per-rider subfolder or DB lookup); add a test that rider A cannot fetch rider B's receipt."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "test_downloads.py test_traversal_is_refused_by_every_handler",
      "scenario": "Only '../secret.txt' is tested; removing '+ os.sep' or replacing realpath with abspath would still pass, allowing sibling-prefix or symlink escapes to regress unnoticed.",
      "fix": "Add absolute-path, sibling-prefix ('../receiptsX/f') and symlink-escape cases; mutate each guard line in a scratch copy and confirm the tests fail."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "downloads.py (whole module) vs request 'download handlers to the rider site'",
      "scenario": "Functions are not wired as handlers; ValueError/FileNotFoundError/IsADirectoryError reach the caller, possibly as 500s leaking absolute paths in debug mode.",
      "fix": "Show route wiring; map refusals and missing files to 404; set Content-Type/Content-Disposition; test missing-file and directory-name requests via the route."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "downloads.py _inside() followed by open()",
      "scenario": "Check-then-use gap: if a docs folder is writable by an attacker, a file swapped for a symlink after the realpath check escapes the folder.",
      "fix": "Keep docs folders read-only to the app and uploaders, or open with O_NOFOLLOW / openat relative to a directory fd."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "test_downloads.py setUp",
      "scenario": "Temp dir never removed, downloads.DOCS globally overwritten and not restored, file handles left unclosed; pollutes other tests importing downloads.",
      "fix": "Use TemporaryDirectory with addCleanup and mock.patch.object for DOCS; use with-blocks for writes."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "downloads.py f.read() in all three handlers",
      "scenario": "Whole file loaded into memory; large map files under concurrent requests inflate memory use.",
      "fix": "Stream the file or use the framework's send-file helper."
    }
  ]
}
```