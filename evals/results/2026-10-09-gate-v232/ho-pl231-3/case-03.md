# Adversarial Diagnostic Review: `downloads.py` (Pedalo rider-site download handlers)

**VERDICT: REWORK.** Two of the three handlers, `receipt` and `manual`, let anyone who can send a file name read any file the server can read. The guard that prevents this already exists in the same file, but only `station_map` uses it.

**CONFIDENCE IN VERDICT: high.** The path-traversal defect follows directly from the code's path joins and does not depend on runtime behaviour. Two things limit confidence in the rest: I had no tools, so I ran nothing, and I could not see the caller or web framework, so error handling and receipt ownership remain open.

## Pass 1: Reconstruct

The work claims to add three download handlers. Each takes a file name from the request and returns the bytes of that file from `DOCS/receipts`, `DOCS/manuals` or `DOCS/maps`.

For this to be correct, these must hold:
- No request-supplied name can resolve outside its own folder, especially since the docs directory sits beside other server files.
- Only the right person can fetch a given file.
- Bad names fail safely.

Load-bearing assumptions, some unstated:
- `name` is untrusted. The module docstring says so: "Names come from the request".
- Some caller wraps these functions into HTTP handlers and converts exceptions into responses.
- Receipts are per-rider, so someone checks ownership.
- `PEDALO_DOCS` points at the intended directory.

## COVERAGE

| Item | Status |
|---|---|
| `request.md` | checked |
| `context.md` | checked |
| `downloads.py` (all 5 units: `DOCS`, `_inside`, `receipt`, `manual`, `station_map`) | checked by reading and hand-tracing; not executed (no tools) |
| Caller / routing / web framework | not checked: not supplied |
| Tests | not checked: none supplied, per context |

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | `downloads.py`, `receipt`: `open(os.path.join(DOCS, "receipts", name), "rb")` | The request-supplied `name` is joined to the folder with no containment check. `os.path.join` discards earlier parts when `name` is absolute, and keeps `..` segments. | Two inputs, with the default `DOCS`: `receipt("/etc/passwd")` gives the path `/etc/passwd`. `receipt("../../../../etc/passwd")` gives `/srv/pedalo/docs/receipts/../../../../etc/passwd`, which is `/etc/passwd`. `receipt("../../<sibling server file>")` reads the server files that the context says sit beside `docs`. Every file the process can read can be downloaded. | **Fix:** `open(_inside("receipts", name), "rb")`. **Repro:** in a scratch copy, set `PEDALO_DOCS=/tmp/x/docs`, create `/tmp/x/secret.txt`, then call `receipt("../../secret.txt")`. Today it returns the contents. After the fix it raises `ValueError`. Also assert that `receipt("/etc/hostname")` raises. | a Y / b Y / c Y / d Y |
| F2 | **Critical** | CONFIRMED | `downloads.py`, `manual`: `open(os.path.join(DOCS, "manuals", name), "rb")` | Same root cause as F1. | `manual("/etc/passwd")` or `manual("../../../../etc/passwd")` returns the file. Manuals are probably public and unauthenticated, so this endpoint is the easier one to reach. | **Fix:** `open(_inside("manuals", name), "rb")`. **Repro:** the same as F1, using `manual(...)`. | a Y / b Y / c Y / d Y |
| F3 | Medium | CONFIRMED (propagation) / PROBABLE (effect) | All three handlers and `_inside` | Exceptions go straight to the caller: `FileNotFoundError`, `IsADirectoryError` (for example a name that is a subfolder), `PermissionError`, `ValueError("outside the folder")`, and `ValueError` for an embedded NUL byte. Nothing maps them to 400 or 404. | A rider asks for a missing receipt and probably gets a 500 rather than a 404. If the framework shows debug tracebacks, the absolute server path in the message reveals the layout. The difference between 404 and 500 also lets an attacker probe which files exist. | Catch `(FileNotFoundError, IsADirectoryError, ValueError)` and raise a not-found error at the handler boundary. Return the same response for "missing" and "outside". **Repro:** call `station_map("nope.png")` and `station_map("")` and observe the raw exceptions. | a Y / b N / c N / d Y |
| F4 | Low | CONFIRMED | Whole module; context says "No tests were supplied" | The only security control, `_inside`, has no test. The fix for F1 and F2 would also rest on it without a test. | Someone later "simplifies" `base + os.sep` to `base`. Then `name="../maps-private/x"` (a sibling folder that shares the `maps` prefix) and `name=""` pass silently. | Add tests for: absolute names, `..` escapes, a sibling-prefix folder, an empty name, `.`, and a symlink inside the folder pointing outside it. Confirm they go red under the mutation `base + os.sep` → `base`, then restore. | a Y / b Y / c N / d N |

**Siblings searched for F1/F2 (root cause: untrusted name joined without `_inside`).** I searched every `open(` and `os.path.join(` in the file. Two of three handlers are affected: `receipt` and `manual`. `station_map` is the only one that uses the guard. No other file was supplied.

**Security boundary for F1/F2:**
- Principal: any unauthenticated or low-trust web client.
- Input: the file-name request parameter.
- Failing control: containment of the name inside its folder, which is absent in these two handlers.
- Boundary crossed: from the web request to the server filesystem outside `DOCS/<folder>`.
- Resource exposed: every file the server process can read, including the adjacent server files named in the context. Likely examples are config files, secrets and source code.

**Strongest defence considered.** "The router validates names before calling these." No router was supplied. The module docstring says names come straight from the request. The author also wrote `_inside` specifically to handle this, which shows they did not expect upstream validation. The finding stands.

## NEEDS VALIDATION

- **Receipt ownership (IDOR).** `receipt(name)` takes no rider identity, so it cannot check that the receipt belongs to the requester. The example names (`2026-09-r1.pdf`) look sequential and guessable. To settle it, find out whether the caller checks that `name` belongs to the authenticated rider before calling `receipt`. If it does not, one rider can download another rider's receipts, which contain personal and payment data. That would be at least High.
- **Symlink TOCTOU in `_inside`.** The path is resolved, then opened separately, so a symlink could be swapped in between. To settle it, find out whether any less-trusted party can write into `DOCS/maps` (or the other folders, once they use `_inside`). If not, this is moot.
- **`PEDALO_DOCS` in production.** To settle it, confirm what value is actually set in deployment, and that it is not `/` or a parent of the server files.

## REFUTED

- **Prefix collision in `_inside`** (`maps` vs `maps-private`). The check is `startswith(base + os.sep)`, so `/…/maps-private/x` does not match `/…/maps/`.
- **Absolute name in `station_map`.** `join(base, "/etc/passwd")` gives `/etc/passwd`, which fails the prefix check and raises.
- **Empty name or `.` in `station_map`.** Both resolve to `base` itself, which does not start with `base + os.sep`, so they are rejected.
- **A symlink inside `maps` pointing out.** `realpath` resolves the link target before the check, so it is rejected.

## WHAT HOLDS UP

- `_inside` is correct for the cases I traced: `..`, absolute paths, symlinks, prefix siblings, empty names and `.`.
- `station_map` uses it properly.
- Files are opened read-only in binary mode, and the handles are closed by `with`.

## UNVERIFIED CLAIMS

- The docstring for `_inside` says it refuses "any name that resolves outside that folder". The hand-trace supports this, but it was not executed. To confirm, run the test set from F4.
- The examples in the docstrings (`receipt('2026-09-r1.pdf')` etc.) work. To confirm, call each one against a populated scratch `DOCS`.

## QUESTIONS FOR THE AUTHOR

1. Why does only `station_map` use `_inside`?
2. Where is receipt ownership enforced, and how does the handler learn which rider is asking?
3. How does the calling framework turn these exceptions into HTTP responses?

## DECISION-MAKER SUMMARY

Do not deploy. Two of the three download endpoints let anyone read arbitrary server files, including the server files next to the docs folder. Routing them through the existing `_inside` guard is a two-line fix, but it needs tests that prove the guard rejects escapes. Receipt ownership is also unresolved: even after the fix, one rider may be able to download another rider's receipts unless the caller checks.

## OWNER SUMMARY

Two of the three new download features have a security hole. Anyone could use them to pull private files off the server, not just the documents they were meant to share. The fix is small and the protection already exists in the same code, but it needs testing before launch. We also still need to confirm that riders can only download their own receipts.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "downloads.py", "status": "seen", "matters": true},
    {"item": "caller/router/framework", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "downloads.py", "kind": "file"},
      {"unit": "_inside", "kind": "function"},
      {"unit": "receipt", "kind": "function"},
      {"unit": "manual", "kind": "function"},
      {"unit": "station_map", "kind": "function"},
      {"unit": "DOCS / PEDALO_DOCS", "kind": "config"}
    ],
    "not_checked": [
      {"unit": "HTTP routing / caller", "reason": "not_supplied"},
      {"unit": "tests", "reason": "not_supplied"},
      {"unit": "runtime execution of any function", "reason": "no_tools"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "downloads.py receipt(): open(os.path.join(DOCS, \"receipts\", name), \"rb\")",
      "scenario": "Request name '/etc/passwd' or '../../../../etc/passwd' (default DOCS) resolves outside DOCS/receipts; the file is returned. Same for server files beside docs.",
      "fix": "open(_inside(\"receipts\", name), \"rb\"), with tests for absolute and '..' names.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "reproduction": "Scratch copy: PEDALO_DOCS=/tmp/x/docs, create /tmp/x/secret.txt, call receipt('../../secret.txt'): contents returned; after fix: ValueError.",
      "security": true,
      "siblings_searched": {"searched": "every open( and os.path.join( in downloads.py", "found": "manual() (F2); station_map() is guarded"},
      "boundary": {"principal": "any web client", "input": "file name request parameter", "control": "path containment (absent)", "crossed": "web request -> server filesystem outside DOCS/receipts", "resource": "any file readable by the server process"}
    },
    {
      "id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "downloads.py manual(): open(os.path.join(DOCS, \"manuals\", name), \"rb\")",
      "scenario": "manual('/etc/passwd') or manual('../../../../etc/passwd') returns the file; manuals are likely public, so it is reachable without login.",
      "fix": "open(_inside(\"manuals\", name), \"rb\"), with the same tests as F1.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "reproduction": "As F1 using manual('../../secret.txt').",
      "security": true,
      "siblings_searched": {"searched": "every open( and os.path.join( in downloads.py", "found": "receipt() (F1)"},
      "boundary": {"principal": "any web client", "input": "file name request parameter", "control": "path containment (absent)", "crossed": "web request -> server filesystem outside DOCS/manuals", "resource": "any file readable by the server process"}
    },
    {
      "id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
      "location": "receipt(), manual(), station_map(), _inside(): no exception handling",
      "scenario": "A missing file, a directory name, a NUL byte or a rejected path raises a raw exception; likely a 500, possibly a traceback leaking server paths, and the 404/500 difference lets an attacker probe which files exist.",
      "fix": "Catch FileNotFoundError, IsADirectoryError and ValueError at the handler boundary and return one uniform not-found response.",
      "answers": {"a": true, "b": false, "c": false, "d": true},
      "reproduction": "Call station_map('nope.png') and station_map(''); observe raw FileNotFoundError and ValueError."
    },
    {
      "id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "module-wide; context.md 'No tests were supplied'",
      "scenario": "The sole containment control _inside is untested; the mutation base + os.sep -> base would let sibling-prefix and empty names through unnoticed.",
      "fix": "Add tests for absolute, '..', sibling-prefix, empty, '.', and an outward symlink; confirm they fail under the mutation, then restore.",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "Apply the mutation in a scratch copy; station_map('../maps-private/x') then passes the check."
    },
    {
      "id": "NV1", "status": "needs_validation", "location": "receipt(name)",
      "suspicion": "No rider identity is passed, so ownership cannot be checked here; receipt names look guessable (IDOR).",
      "unresolved_fact": "Does the caller verify that the receipt belongs to the authenticated rider before calling receipt()?"
    },
    {
      "id": "NV2", "status": "needs_validation", "location": "_inside() then open()",
      "suspicion": "Symlink-swap race between realpath and open.",
      "unresolved_fact": "Can any less-trusted party write into the DOCS subfolders?"
    },
    {
      "id": "NV3", "status": "needs_validation", "location": "DOCS = os.environ.get(\"PEDALO_DOCS\", ...)",
      "suspicion": "A misconfigured PEDALO_DOCS could widen what is served.",
      "unresolved_fact": "The value set in production."
    }
  ],
  "refuted": [
    {"id": "R1", "candidate": "Prefix collision maps vs maps-private in _inside", "evidence": "Check is startswith(base + os.sep)."},
    {"id": "R2", "candidate": "Absolute name bypasses station_map", "evidence": "join gives the absolute path, realpath keeps it outside base, ValueError raised."},
    {"id": "R3", "candidate": "Empty name or '.' returns the folder in station_map", "evidence": "Both resolve to base, which does not start with base + os.sep, so they are rejected."},
    {"id": "R4", "candidate": "Symlink inside maps pointing out", "evidence": "realpath resolves the target before the check, so it is rejected."}
  ]
}
```