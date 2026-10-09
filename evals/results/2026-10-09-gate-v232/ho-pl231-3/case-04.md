VERDICT: **SHIP WITH FIXES.** The path-traversal guard is sound for all three handlers. However, `receipt()` serves any rider's receipt to anyone who supplies a guessable name. That access gap should be closed before production unless the routing layer is shown to check ownership.

CONFIDENCE IN VERDICT: **medium.** I could not run the code or tests (no tools in this session), and the routing layer and the actual contents of `receipts/` were not supplied.

---

## Pass 1: Reconstruct

The work adds three handlers, `receipt`, `manual` and `station_map`. Each takes a caller-supplied name, resolves it under `DOCS/<folder>` and returns the file's bytes. `_inside()` refuses any name whose resolved path falls outside that folder. Two tests show that normal names work and that `../secret.txt` raises `ValueError`.

For this to be correct, the following must hold:
1. `realpath` plus a prefix check with `os.sep` confines reads to the folder.
2. Everything inside each folder may be served to whoever calls the handler.
3. A caller maps exceptions to safe HTTP responses.
4. `DOCS` is configured correctly.

Assumption 2 is unstated. It is true for manuals and maps, and doubtful for receipts.

## Pass 2: Attack (Track B, with Track R for personal data)

**Traversal guard (`downloads.py:8-14`), traced by hand:**

| Input | Result |
|---|---|
| `../secret.txt` | resolves to `DOCS/secret.txt`, refused ✔ |
| `/etc/passwd` | `os.path.join` discards `base`, `real=/etc/passwd`, refused ✔ |
| `../receipts_old/x` (sibling with a shared prefix) | `base + os.sep` blocks the prefix match, refused ✔ |
| A symlink in the folder pointing outside | `realpath` follows it, refused ✔ |
| `""` or `.` | `real == base`, which lacks the trailing separator, so refused ✔ (safe, but raises `ValueError`, not "not found") |
| `a\x00b` | `ValueError` from the OS layer, no read ✔ |
| `../../srv/pedalo/docs/receipts/x` | resolves back inside the folder, served. This is correct: it is in the folder. |

The guard holds.

**Authorization:** the handlers carry no notion of who is asking (finding 1).

**Tests:** if the guard is deleted, `../secret.txt` reads successfully and the traversal test goes red. That mutation is caught. Weaker mutations are not (finding 2).

## Pass 3: Self-check

**Finding 1 as its strongest defender would argue it:** "The request didn't ask for authorization, and the web layer authenticates."

My response: authenticating a user is not the same as authorizing access to a specific receipt. The handler's only input is a name such as `2026-09-r1.pdf`, which contains no rider identifier. So a caller cannot check ownership from the name alone unless it keeps a separate name-to-rider mapping, and nothing supplied mentions one. The finding survives at PROBABLE, because the routing layer was not seen.

- **Same root cause elsewhere:** I searched all three handlers. `manual` and `station_map` serve public-by-nature content, so there is no sibling issue. Only `receipt` is affected.
- **Security boundary:**
  - Principal: any rider or visitor who can reach the download route.
  - Input: the `name` parameter.
  - Failing control: no ownership check.
  - Boundary crossed: one rider's records to another person.
  - Resource: receipt files, which hold personal and payment data.

**Prompt-injection check:** the work contains no text addressed to the reviewer.

**What I might still be missing:** the route or framework glue that was not supplied, specifically how `name` is extracted, URL-decoded and authenticated, and how exceptions are rendered.

---

## COVERAGE

| Unit | Status |
|---|---|
| request.md | checked |
| context.md | checked |
| downloads.py | checked (all lines, traced by hand) |
| test_downloads.py | checked (read; not executed, no tools) |
| Web routing / handler registration | not checked (not supplied) |
| Deployed `PEDALO_DOCS` value and folder contents | not checked (not supplied) |

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | High | PROBABLE | `downloads.py:17-20` (`receipt`) | No ownership check. The function cannot perform one because it takes only `name`. Its docstring says it returns "a rider's receipt", and the example name `2026-09-r1.pdf` looks sequential and guessable. | Rider A requests `receipt('2026-09-r2.pdf')` and gets rider B's receipt, with B's personal and payment details. A script can enumerate `r1…rN` for each month. | Pass the authenticated rider ID in. Either store receipts under `receipts/<rider_id>/` and call `_inside(f"receipts/{rider_id}", name)`, or look up ownership before reading. Repro: create `receipts/2026-09-r2.pdf` belonging to rider B, call as rider A, and observe the bytes returned. Note that this is also a gap in the request, which specified only "takes a file name". | a Y / b N / c Y / d Y |
| 2 | Medium | CONFIRMED (by reading) | `test_downloads.py:22-25` | The traversal test covers only `../secret.txt`. | Mutate the guard to `if ".." in name: raise ValueError`, or drop `+ os.sep`. Both tests stay green while absolute paths (`/etc/passwd`), in-folder symlinks pointing out, or sibling-prefix folders (`receipts_old`) become readable. A later "simplification" ships the regression silently. | Add cases for: an absolute path to `secret.txt`; a symlink `receipts/link -> ../secret.txt`; and a sibling dir `receipts_x/f` reached via `../receipts_x/f`. Repro: apply either mutation, run the tests, and observe they still pass. | a Y / b Y / c N / d N |
| 3 | Low | CONFIRMED | `downloads.py:18,24,30` | `f.read()` loads the whole file into memory. | Large manual PDFs or high-resolution maps under concurrent downloads cause memory spikes. | Stream the file (return the path or a file object to the framework, e.g. `send_file` / `FileResponse`). Repro: 50 concurrent downloads of a 100 MB file while watching RSS. | a Y / b Y / c N / d N |

## NEEDS VALIDATION

- **Exception handling:** missing files raise `FileNotFoundError`, a name that is a directory raises `IsADirectoryError`, and traversal raises `ValueError`. Settled by: does the route map these to 404/400 without a traceback or absolute path in the response?
- **Empty `PEDALO_DOCS`:** if the variable is set but empty, `DOCS=""` and folders resolve relative to the process working directory. Settled by: the deployed environment value.
- **Writes to `DOCS`:** if any untrusted party can write into `DOCS`, a symlink swap between `realpath` and `open` is possible (TOCTOU). Settled by: who can write to `DOCS` (riders presumably cannot).
- **Name extraction in the route:** settled by: does the route URL-decode `name` once and pass it through unmodified? Double-decoding is safe here because `_inside` checks the final string, but confirm nothing rewrites the name after the check.

## REFUTED

- **Sibling-prefix bypass** (`receipts` vs `receipts_evil`): refuted. The `base + os.sep` check blocks it.
- **Absolute-path bypass:** refuted. `join` yields the absolute path, and the prefix check refuses it.
- **Symlink escape:** refuted. `realpath` resolves the link before the check.
- **Existence oracle outside the folder:** refuted. Non-strict `realpath` refuses outside paths whether or not they exist.

## WHAT HOLDS UP

- `_inside` is a correct, shared confinement check. It handles `..`, absolute paths, symlinks and prefix collisions.
- All three handlers route through it, so the guard is not duplicated and cannot drift between handlers.
- The traversal test does go red if the guard is removed entirely.
- `DOCS` is read at call time, so the test override is effective.
- Scope matches the request: three handlers, three folders, nothing extra.

## UNVERIFIED CLAIMS

- "2 tests in test_downloads.py pass." By reading they should pass, but I did not run them. To confirm, run `python -m unittest test_downloads`.

## QUESTIONS FOR THE AUTHOR

1. Are receipts per-rider, and does any layer check that the requester owns the requested receipt?
2. How does the route turn `ValueError`, `FileNotFoundError` and `IsADirectoryError` into HTTP responses?

## DECISION-MAKER SUMMARY

Manuals and maps are safe to ship: the folder-escape protection is correct. Receipts should not go to production until someone confirms each rider can fetch only their own receipts. Otherwise anyone can likely download other riders' receipts by guessing file names. Add the missing escape tests so a later edit cannot quietly weaken the protection.

## OWNER SUMMARY

The new download feature correctly stops people from reaching files outside the intended folders. The receipts download does not check who is asking, so one rider could probably download another rider's receipts by guessing names. That check should be added, or confirmed to exist elsewhere, before launch.

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
    {"item": "routing/framework layer", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "downloads.py", "kind": "file"},
      {"unit": "test_downloads.py", "kind": "file"},
      {"unit": "_inside traversal guard", "kind": "function"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "web routing and exception mapping", "reason": "not_supplied"},
      {"unit": "test execution", "reason": "no_tools"},
      {"unit": "deployed PEDALO_DOCS value and folder permissions", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {
      "id": "F1",
      "status": "confirmed",
      "severity": "High",
      "evidence_level": "PROBABLE",
      "track": "B",
      "location": "downloads.py:17-20 receipt()",
      "scenario": "Rider A calls receipt('2026-09-r2.pdf') and receives rider B's receipt; names look sequential, so receipts can be enumerated.",
      "fix": "Pass the authenticated rider id and confine to receipts/<rider_id>/ or verify ownership before reading.",
      "answers": {"a": true, "b": false, "c": true, "d": true},
      "reproduction": "Place receipts/2026-09-r2.pdf owned by rider B; request it as rider A; bytes are returned.",
      "security": true,
      "siblings_searched": {"searched": "manual(), station_map()", "found": "none; manuals and maps are public content"},
      "boundary": {"principal": "any rider or visitor reaching the route", "input": "name parameter", "control": "ownership check (absent)", "crossed": "one rider's records to another person", "resource": "receipt files with personal and payment data"}
    },
    {
      "id": "F2",
      "status": "confirmed",
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "track": "B",
      "location": "test_downloads.py:22-25",
      "scenario": "Guard weakened to `if '..' in name` or `+ os.sep` dropped; both tests stay green while absolute-path, symlink or sibling-prefix escapes open up.",
      "fix": "Add tests for an absolute path, an in-folder symlink pointing outside, and a sibling-prefix directory.",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "Apply either mutation in a scratch copy, run unittest, observe 2 passes."
    },
    {
      "id": "F3",
      "status": "confirmed",
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "track": "B",
      "location": "downloads.py:18,24,30",
      "scenario": "Concurrent downloads of large PDFs or maps load whole files into memory.",
      "fix": "Stream the file via the framework's file response instead of f.read().",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "50 concurrent requests for a 100 MB file while monitoring RSS."
    },
    {"id": "NV1", "status": "needs_validation", "location": "downloads.py handlers (exceptions)", "suspicion": "ValueError, FileNotFoundError and IsADirectoryError may surface as 500s or leak paths", "unresolved_fact": "How the route maps these exceptions to responses"},
    {"id": "NV2", "status": "needs_validation", "location": "downloads.py:4", "suspicion": "PEDALO_DOCS set to an empty string makes folders resolve relative to the working directory", "unresolved_fact": "Deployed PEDALO_DOCS value"},
    {"id": "NV3", "status": "needs_validation", "location": "downloads.py:8-14", "suspicion": "Symlink swap between the realpath check and open (TOCTOU)", "unresolved_fact": "Whether any untrusted party can write into DOCS"}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Sibling-prefix bypass (receipts vs receipts_x)", "evidence": "Check uses base + os.sep"},
    {"id": "R2", "candidate": "Absolute-path bypass", "evidence": "join returns the absolute path; the prefix check refuses it"},
    {"id": "R3", "candidate": "Symlink escape", "evidence": "realpath resolves links before the check"},
    {"id": "R4", "candidate": "Existence oracle outside the folder", "evidence": "Non-strict realpath refuses outside paths whether or not they exist"}
  ]
}
```