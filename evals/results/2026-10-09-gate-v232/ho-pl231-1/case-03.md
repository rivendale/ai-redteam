VERDICT: **REJECT**. Two of the three handlers, `receipt` and `manual`, accept a raw request-supplied name and open it with no containment check. Any caller can read any file the server process can read, including the server files that sit beside the docs directory.

CONFIDENCE IN VERDICT: **high**. The defect is visible directly in the code and does not depend on runtime behaviour. What limits confidence: I had no tools, so nothing was executed. I also cannot see the routing layer, so I don't know how these functions are exposed or whether anything upstream filters names.

---

## Pass 1: Reconstruct

The work adds three functions, `receipt`, `manual` and `station_map`. Each takes a file name from the request and returns that file's bytes from `DOCS/receipts`, `DOCS/manuals` or `DOCS/maps`. A helper, `_inside`, resolves the path and refuses names that land outside the target folder.

For the work to be correct, these must be true:
- Every handler confines `name` to its own folder.
- `name` is untrusted. The module docstring says so: "Names come from the request."
- The caller turns exceptions into sensible HTTP responses.

Unstated assumptions:
- Authorization, meaning which rider may fetch which receipt, is handled elsewhere.
- Files are small enough to read fully into memory.

## Pass 2: Attack (Track B, with Track R notes for receipts)

**Tracing `receipt` / `manual`** (`downloads.py:18-26`):
- The path is built as `os.path.join(DOCS, "receipts", name)`, with no normalization and no check.
- `name = "../../../etc/passwd"` resolves to `/srv/pedalo/docs/receipts/../../../etc/passwd`, which `open` follows to `/etc/passwd`.
- `name = "../../app/settings.py"` reaches server files next to docs, which is exactly the stake the context names.
- `name = "/etc/passwd"`: `os.path.join` discards every earlier component when it meets an absolute one, so this opens `/etc/passwd` directly. No `..` is needed.
- `name = "../receipts/../manuals/x.pdf"` crosses between folders.

**Tracing `_inside` / `station_map`** (`downloads.py:8-14, 29-32`):
- `../x` resolves to the parent folder and fails `startswith(base + os.sep)`. Rejected.
- `/etc/passwd`: the join yields `/etc/passwd`, which is not under base. Rejected.
- A sibling with the same prefix, such as `maps2/...`, is blocked because of the `+ os.sep`.
- A symlink inside `maps` pointing outward is caught, because `realpath` resolves it before the check.
- An empty string or `.` gives `real == base`, which fails the check and raises `ValueError`. Acceptable.
- A NUL byte makes `open` raise `ValueError`. Acceptable.
- `subdir/` (a directory) raises `IsADirectoryError`, which is unhandled (see NV2).
- Check-then-open is a TOCTOU window, but exploiting it requires write access to `maps/`. That is out of scope for a rider.

**Hallucination check:** `os.path.realpath`, `os.path.join` and `os.sep` all exist and behave as the code assumes.

**Requirement fit:** All three handlers exist and return file bytes. Containment, which the helper's own docstring makes the intended contract, is applied to only one of them.

## Pass 3: Self-check

**Defending F1 as its author would:** Maybe the router already strips `/` and `..`. Nothing supplied shows that, and the module docstring says names come straight from the request. The author also wrote `_inside`, which shows they knew the threat and then failed to apply it. The finding survives.

**Sibling search:** I checked every `open(` call in the file, three in total. `receipt` and `manual` both build the path with a raw join; only `station_map` uses `_inside`. There is no other file I/O.

**Security boundary for F1:**
- Principal: any client that can reach the download endpoint, possibly unauthenticated.
- Input: the `name` request parameter.
- Failing control: no containment check (`_inside` is not called).
- Boundary crossed: from `DOCS/receipts` or `DOCS/manuals` to the whole filesystem readable by the server process.
- Resource: server source, config and secrets next to docs, system files, and every rider's receipts.

**Most serious thing I might still be missing:** the routing and authentication layer, which was not supplied. Receipts are per-rider personal data. Even with containment fixed, `receipt('2026-09-r1.pdf')` suggests guessable names, so one rider may be able to download another's receipts if no ownership check exists upstream (NV1).

---

## COVERAGE

| Unit | Status |
|---|---|
| request.md | checked |
| context.md | checked |
| downloads.py (all of it: `DOCS`, `_inside`, `receipt`, `manual`, `station_map`) | checked by reading and tracing; **not executed** (no tools) |
| Routing / web framework wiring | not checked, not supplied |
| Tests | not checked, none exist (the context confirms this) |

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | `downloads.py:20` (`receipt`) and `downloads.py:26` (`manual`): `open(os.path.join(DOCS, "<folder>", name), "rb")` | Path traversal. The request-supplied `name` is joined and opened with no containment check. `_inside` exists but is used only by `station_map`. | `receipt("../../../etc/passwd")`, `manual("/etc/shadow")` (the absolute name overrides the join) or `receipt("../../app/.env")` returns arbitrary files the server can read, including the server files beside docs. Any rider's receipt is also reachable by path. | **Fix:** route both through `_inside("receipts", name)` and `_inside("manuals", name)`, the same as `station_map`. **Repro (scratch copy):** set `PEDALO_DOCS=$tmp/docs`, create `$tmp/docs/receipts/` and `$tmp/secret.txt`. Then `receipt("../../secret.txt")` returns the secret, `manual("/etc/hostname")` returns the hostname, and after the fix both raise `ValueError`. | a Y, b Y, c Y (security breach and customer data), d Y |
| F2 | Medium | CONFIRMED | Whole module; no tests supplied | The containment rule has no tests, so no test ever went red and none caught that two of three handlers skip it, which is how F1 shipped. | A future refactor, or another handler like F1, drops `_inside` silently. | Add a parametrized test across all three handlers covering `../x`, `/etc/hostname`, `..%2f`-decoded forms, a symlink pointing outward, a sibling-prefix folder (`maps2`), and a valid name. Confirm the test fails against the current `receipt`/`manual` (mutation already present) and passes after the fix. | a Y, b Y, c N, d Y |
| F3 | Low | CONFIRMED | `downloads.py:21, 27, 32`: `f.read()` | The whole file is read into memory per request. | Large manuals or maps under concurrent downloads push up memory use; at 100x load this risks OOM. | Stream the file (chunked response, or the framework's send-file) instead of returning bytes. **Repro:** call `manual()` on a 500 MB file in a scratch dir and observe RSS. | a Y, b Y, c N, d N |

## NEEDS VALIDATION

- **NV1 (`receipt`, authorization):** Receipts are per-rider. Does the caller check that the logged-in rider owns the requested receipt? If not, guessable names like `2026-09-r1.pdf` let any rider fetch others' receipts, even after F1 is fixed. *Settled by:* the route or middleware code for the receipts endpoint.
- **NV2 (all handlers, error mapping):** `ValueError`, `FileNotFoundError`, `IsADirectoryError` and `PermissionError` all propagate. If the framework renders tracebacks, server paths leak, and missing files return 500 instead of 404. *Settled by:* the framework's error handling config in production (debug off? exception-to-404 mapping?).
- **NV3 (requirement fit):** "Download handlers" may mean wired HTTP routes with content-type and `Content-Disposition` headers. The work provides plain functions only. *Settled by:* asking whether routing was expected in this change.

## REFUTED

- **R1: `_inside` is bypassable with a sibling folder that shares the prefix (`maps` vs `maps_private`).** Refuted: the check uses `base + os.sep`, so `/…/maps_private/x` does not start with `/…/maps/`.
- **R2: `_inside` is bypassable with an absolute `name`.** Refuted: the join yields the absolute path, `realpath` leaves it outside base, and the check rejects it.
- **R3: `_inside` is bypassable through a symlink inside `maps`.** Refuted: `realpath` resolves symlinks before the comparison.

## WHAT HOLDS UP

`_inside` is a correct containment check for Linux. It resolves symlinks and `..`, handles absolute names, and guards against prefix confusion. `station_map` is safe against traversal. The `DOCS` environment override is reasonable.

## UNVERIFIED CLAIMS

- The `_inside` docstring says it is "refusing any name that resolves outside that folder". This is true by my trace, but it was never run. *Confirm:* run the F2 test suite against it.
- The example names in the docstrings resolve to real files. *Confirm:* list `/srv/pedalo/docs/*`.

## QUESTIONS FOR THE AUTHOR

1. Was leaving `_inside` out of `receipt` and `manual` deliberate? Is there any upstream sanitization of `name`? (If there is robust filtering, F1 drops, but the fix is still cheap.)
2. Where is the ownership check for receipts (NV1)?

## DECISION-MAKER SUMMARY

Do not deploy. Two of the three download endpoints let anyone read arbitrary server files, including the secrets next to the docs folder and other riders' receipts. The fix is a two-line change to reuse the existing safe helper, plus traversal tests. Confirm separately that receipts are restricted to their owner.

## OWNER SUMMARY

Two of the three new download features let a visitor read files on the server that were never meant to be public, including private configuration and other customers' receipts. The third feature is built safely, and the same safe approach can be applied to the other two quickly. This should be fixed and tested before release, and someone should confirm that customers can download only their own receipts.

```json
{
  "schema_version": "2.3",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "downloads.py", "status": "seen", "matters": true},
    {"item": "routing/auth layer", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "downloads.py", "kind": "file"},
      {"unit": "downloads._inside", "kind": "function"},
      {"unit": "downloads.receipt", "kind": "function"},
      {"unit": "downloads.manual", "kind": "function"},
      {"unit": "downloads.station_map", "kind": "function"},
      {"unit": "PEDALO_DOCS default", "kind": "config"}
    ],
    "not_checked": [
      {"unit": "routing and authentication layer", "reason": "not_supplied"},
      {"unit": "tests", "reason": "not_supplied"},
      {"unit": "runtime execution of downloads.py", "reason": "no_tools"}
    ]
  },
  "findings": [
    {
      "id": "F1",
      "status": "confirmed",
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "track": "B",
      "location": "downloads.py:20 receipt and downloads.py:26 manual: open(os.path.join(DOCS, folder, name), 'rb')",
      "scenario": "A request with name '../../../etc/passwd', '/etc/shadow' (an absolute name overrides the join) or '../../app/.env' makes receipt() or manual() return arbitrary files readable by the server process, including server files beside the docs directory and any rider's receipt.",
      "fix": "Use _inside('receipts', name) and _inside('manuals', name) as station_map does.",
      "reproduction": "Scratch copy: PEDALO_DOCS=$tmp/docs, mkdir $tmp/docs/receipts, write $tmp/secret.txt; receipt('../../secret.txt') returns the secret; manual('/etc/hostname') returns the hostname; after the fix both raise ValueError.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "security": true,
      "siblings_searched": {
        "searched": "every open() call in downloads.py (3)",
        "found": "receipt and manual both unguarded; station_map guarded by _inside"
      },
      "boundary": {
        "principal": "any client able to reach the download endpoints",
        "input": "name request parameter",
        "control": "path containment check (_inside) not applied",
        "crossed": "DOCS/receipts and DOCS/manuals to the whole readable filesystem",
        "resource": "server source/config/secrets beside docs, system files, all riders' receipts"
      }
    },
    {
      "id": "F2",
      "status": "confirmed",
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "track": "B",
      "location": "downloads.py (whole module); no tests supplied",
      "scenario": "The containment rule is untested, so handlers skipping it (F1) or future regressions pass unnoticed.",
      "fix": "Add a parametrized traversal test over all three handlers (../, absolute path, symlink out, sibling-prefix folder, valid name); confirm it fails on the current receipt/manual and passes after the fix.",
      "reproduction": "Write the test; run it against the current code: the receipt/manual cases fail, which is the mutation proof.",
      "answers": {"a": true, "b": true, "c": false, "d": true}
    },
    {
      "id": "F3",
      "status": "confirmed",
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "track": "B",
      "location": "downloads.py:21, 27, 32 f.read()",
      "scenario": "Concurrent downloads of large manuals or maps load each whole file into memory; under heavy load this risks memory exhaustion.",
      "fix": "Stream the file in chunks or use the framework's send-file.",
      "reproduction": "In a scratch dir, call manual() on a 500 MB file and observe process RSS growth.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "NV1",
      "status": "needs_validation",
      "location": "downloads.py:18 receipt",
      "suspicion": "No ownership check; guessable receipt names let one rider fetch another's receipt even after F1 is fixed.",
      "unresolved_fact": "Whether the route or middleware verifies that the authenticated rider owns the requested receipt."
    },
    {
      "id": "NV2",
      "status": "needs_validation",
      "location": "downloads.py all handlers",
      "suspicion": "Uncaught ValueError/FileNotFoundError/IsADirectoryError may surface as 500s or leak server paths in tracebacks.",
      "unresolved_fact": "The framework's production error handling and debug setting."
    },
    {
      "id": "NV3",
      "status": "needs_validation",
      "location": "downloads.py module scope",
      "suspicion": "'Download handlers' may require wired HTTP routes with headers; only plain functions were delivered.",
      "unresolved_fact": "Whether route wiring was in scope for this change."
    }
  ],
  "refuted": [
    {"id": "R1", "candidate": "_inside bypass via sibling folder with the same prefix", "evidence": "Check compares against base + os.sep."},
    {"id": "R2", "candidate": "_inside bypass via absolute name", "evidence": "The join yields the absolute path, realpath keeps it outside base, and startswith fails."},
    {"id": "R3", "candidate": "_inside bypass via a symlink inside maps", "evidence": "realpath resolves symlinks before the comparison."}
  ]
}
```