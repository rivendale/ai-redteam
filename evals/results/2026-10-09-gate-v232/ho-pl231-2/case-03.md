**VERDICT: REWORK.** Two of the three handlers pass an untrusted file name straight to `open()`, so any caller can read files outside the docs directory, including the server files that sit beside it.

**CONFIDENCE IN VERDICT: high.** The traversal follows directly from the code. Confidence is limited only because I had no tools and could not run anything, and because I could not see the web layer that calls these functions.

## Pass 1: Reconstruct

The work adds three functions, `receipt`, `manual` and `station_map`. Each takes a file name from the request and returns the bytes of that file from `DOCS/<folder>`. The module docstring says "Names come from the request", so the author treats `name` as untrusted. A guard, `_inside`, resolves the path and refuses anything outside the folder.

For the work to be correct, these must hold:

1. Every handler confines `name` to its own folder.
2. Some other layer checks who may read which file. This matters most for receipts, which are personal.
3. A framework turns these functions into HTTP handlers and maps their errors to sensible responses.
4. The files are small enough to read whole.

Assumption 1 is false for two of the three handlers.

## COVERAGE

| Unit | Status |
|---|---|
| request.md | checked |
| context.md | checked |
| downloads.py: `DOCS`, `_inside`, `receipt`, `manual`, `station_map` | checked (read and traced by hand, not executed; no tools) |
| Web routing and auth layer that calls these functions | not checked: not supplied |
| Tests | not checked: none supplied (the context says so) |

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | `downloads.py`, `receipt`: `open(os.path.join(DOCS, "receipts", name), "rb")` | The request-supplied `name` is joined and opened with no containment check. `_inside` exists in the same file but is not used. | (1) `name="../../../etc/passwd"` opens `/srv/pedalo/docs/receipts/../../../etc/passwd`, which is `/etc/passwd`. (2) `name="../../app/config.py"` reads server files beside docs, as the context warns. (3) `name="/etc/shadow"`: `os.path.join` throws away every earlier part when given an absolute component, so this opens `/etc/shadow` directly, with no `..` needed. | Use `open(_inside("receipts", name), "rb")`. Repro: create `tmp/docs/receipts`, `tmp/secret.txt`, set `PEDALO_DOCS=tmp/docs`. Today, `receipt("../../secret.txt")` returns the secret. After the fix it must raise `ValueError`. Add the same test for the absolute-path form. | a Y / b Y / c Y / d Y |
| F2 | Critical | CONFIRMED | `downloads.py`, `manual`: `open(os.path.join(DOCS, "manuals", name), "rb")` | Same root cause as F1 in the manuals handler. | `manual("../../../etc/passwd")` or `manual("/etc/passwd")` returns that file. | Use `open(_inside("manuals", name), "rb")`. Repro: the F1 test, pointed at `manual`. | a Y / b Y / c Y / d Y |
| F3 | Medium | PROBABLE | All three handlers | Nothing handles errors. `FileNotFoundError`, `IsADirectoryError` (for example `station_map("sub")`), `ValueError("outside the folder")`, and `ValueError` for a name containing a NUL byte all propagate. Whether they become a 500 response, and whether the traceback (with absolute server paths) reaches the client, depends on the unseen framework. | A rider asks for a missing receipt and gets a 500, possibly with the full path. Logs cannot tell a probing attacker from an ordinary 404. | Catch `FileNotFoundError` and `IsADirectoryError` and return 404. Catch `ValueError` and return 400 or 404, and log it as a rejected path. Test each error class. | a Y / b N / c N / d Y |
| F4 | Low | CONFIRMED | Whole module versus the request ("Add three download handlers to the rider site") | These are plain functions. No routes, content-type, or `Content-Disposition` header are wired. The deliverable may be presented as "handlers added" when integration is still to do. | The site never exposes them, or serves PDFs and PNGs with the wrong type. | Wire the routes, or state in the PR that integration is a separate step. | a Y / b Y / c N / d N |
| F5 | Low | CONFIRMED | `f.read()` in all three handlers | Each file is read whole into memory. | Large manuals or maps under concurrent load raise memory use. This is unlikely to matter at current scale. | Stream the file, for example with the framework's `send_file`. | a Y / b Y / c N / d N |

**Re-examining F1 and F2 as their strongest defender would.**

- *"The framework sanitizes the path parameter."* Many routers stop a `/` inside a single path segment. They do not stop query-string or form values, and they do not stop URL-encoded `%2F` in every configuration. The function has to be safe on its own: its docstring says the names come from the request.
- *"Only trusted callers use it."* Nothing in the request or context says so.

Both findings stand.

**Sibling search.** I checked every `open()` and `os.path.join` in the file: three `open` calls, two unguarded (F1, F2) and one guarded (`station_map`). No other file access exists.

**Security boundary for F1 and F2.**

| Element | Value |
|---|---|
| Principal | Any client of the rider site, possibly unauthenticated |
| Input | The `name` request parameter |
| Failing control | Missing containment check (`_inside` not called) |
| Boundary crossed | `DOCS/receipts` or `DOCS/manuals` to the rest of the server filesystem readable by the process |
| Resources | Server configuration and secrets beside docs, system files, all riders' receipts |

## NEEDS VALIDATION

- **NV1: authorization on receipts.** `receipt(name)` has no notion of which rider is asking. The docstring example, `2026-09-r1.pdf`, suggests guessable sequential names. If no outer layer checks that the requested receipt belongs to the signed-in rider, any rider can enumerate other riders' receipts, which hold personal and payment data. *Settling fact:* does the route verify the receipt's owner against the session before calling `receipt`? If not, this is Critical.
- **NV2: symlink swap between check and open in `_inside`.** An attacker could swap a symlink between `realpath` and `open`. *Settling fact:* can any lower-trust process write into `DOCS/maps`? If not, there is no risk.

## REFUTED

- **R1: "`_inside` can be bypassed by a sibling folder such as `maps2` or `maps_old`."** Refuted. The check is `startswith(base + os.sep)`, not `startswith(base)`.
- **R2: "`_inside` is bypassed by absolute names, `..`, or symlinks."** Refuted. `os.path.join(base, "/etc/x")` gives `/etc/x`, `realpath` resolves `..` and symlinks, and the prefix check then rejects all of these.
- **R3: "An empty name or `.` returns the folder."** Refuted. `real == base` does not start with `base + os.sep`, so it is rejected.

## WHAT HOLDS UP

`_inside` is a correct containment guard. It resolves both the base and the target with `realpath` and compares against the base plus a separator, so it handles `..`, absolute names, symlinks, sibling-prefix folders, and empty names. `station_map` is safe against traversal. `DOCS` coming from an environment variable with a fixed default is reasonable.

## UNVERIFIED CLAIMS

- **The docstring claim that `_inside` refuses "any name that resolves outside that folder".** I traced it by hand but did not run it. To confirm, run the tests in R1 to R3 against a temporary directory tree with a symlink pointing out of `maps`.
- **Test coverage.** None exists. Per rule 5, any test added must be mutation-checked: remove the `_inside` call from `station_map` and confirm the traversal test fails.

## QUESTIONS FOR THE AUTHOR

1. Why do `receipt` and `manual` not call `_inside`? Was that deliberate?
2. What checks that a receipt belongs to the requesting rider (NV1)?
3. Which framework calls these functions, and how does it map their exceptions to HTTP responses?

## DECISION-MAKER SUMMARY

Do not deploy. The receipt and manual downloads let any caller read arbitrary server files, including the files that sit beside the docs directory. The fix is two one-line changes plus tests, but receipts also need a confirmed ownership check, or riders can read each other's receipts even after the path fix.

## OWNER SUMMARY

Two of the three new download features can be tricked into handing out any file on the server, including private configuration, so they must not go live yet. The third feature, for station maps, is protected correctly, and the same protection only needs to be applied to the other two. We also need to confirm that riders can only download their own receipts.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "downloads.py", "status": "seen", "matters": true},
    {"item": "web routing / auth layer", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "downloads.py:_inside", "kind": "function"},
      {"unit": "downloads.py:receipt", "kind": "function"},
      {"unit": "downloads.py:manual", "kind": "function"},
      {"unit": "downloads.py:station_map", "kind": "function"},
      {"unit": "downloads.py:DOCS", "kind": "config"}
    ],
    "not_checked": [
      {"unit": "routing/auth layer calling these functions", "reason": "not_supplied"},
      {"unit": "tests", "reason": "not_supplied"},
      {"unit": "runtime execution of any path", "reason": "no_tools"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "downloads.py receipt(): open(os.path.join(DOCS, \"receipts\", name), \"rb\")",
      "scenario": "receipt('../../../etc/passwd') or receipt('/etc/shadow') (os.path.join discards earlier parts for an absolute component) or receipt('../../<server file beside docs>') returns that file to the caller.",
      "fix": "open(_inside(\"receipts\", name), \"rb\"); add traversal and absolute-path tests.",
      "reproduction": "PEDALO_DOCS=tmp/docs with tmp/docs/receipts and tmp/secret.txt; receipt('../../secret.txt') returns the secret now and must raise ValueError after the fix.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "security": true,
      "siblings_searched": {"searched": "every open()/os.path.join in downloads.py (3 open calls)", "found": "manual() unguarded (F2); station_map() guarded"},
      "boundary": {"principal": "any rider-site client", "input": "name request parameter", "control": "containment check missing (_inside not called)", "crossed": "DOCS/receipts to server filesystem", "resource": "server config/secrets beside docs, system files, other riders' receipts"}
    },
    {
      "id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "downloads.py manual(): open(os.path.join(DOCS, \"manuals\", name), \"rb\")",
      "scenario": "manual('../../../etc/passwd') or manual('/etc/passwd') returns that file.",
      "fix": "open(_inside(\"manuals\", name), \"rb\"); add the same tests as F1.",
      "reproduction": "Same harness as F1 using manual('../../secret.txt').",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "security": true,
      "siblings_searched": {"searched": "every open()/os.path.join in downloads.py", "found": "receipt() unguarded (F1); station_map() guarded"},
      "boundary": {"principal": "any rider-site client", "input": "name request parameter", "control": "containment check missing (_inside not called)", "crossed": "DOCS/manuals to server filesystem", "resource": "server config/secrets beside docs, system files"}
    },
    {
      "id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
      "location": "receipt/manual/station_map: no exception handling",
      "scenario": "A missing file, a directory name, a rejected path or a NUL byte propagates FileNotFoundError, IsADirectoryError or ValueError, likely becoming a 500 that may expose server paths; probing is indistinguishable from ordinary misses.",
      "fix": "Map FileNotFoundError/IsADirectoryError to 404 and ValueError to 400/404 with a log entry; test each.",
      "reproduction": "station_map('missing.png') raises FileNotFoundError; station_map('../x') raises ValueError; observe the HTTP response in the framework.",
      "answers": {"a": true, "b": false, "c": false, "d": true}
    },
    {
      "id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "downloads.py (whole module) vs request 'Add three download handlers to the rider site'",
      "scenario": "Plain functions with no routes, content-type or Content-Disposition; the site does not expose them, or serves files with the wrong type.",
      "fix": "Wire routes and headers, or state that integration is a separate step.",
      "reproduction": "Search the codebase for route registrations referencing receipt/manual/station_map; none are in the supplied work.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "f.read() in all three handlers",
      "scenario": "Large manuals or maps under concurrent requests are held fully in memory.",
      "fix": "Stream the file (framework send_file or chunked read).",
      "reproduction": "Request a multi-hundred-MB file concurrently and observe process RSS.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "NV1", "status": "needs_validation",
      "location": "downloads.py receipt()",
      "suspicion": "No ownership check; guessable receipt names (2026-09-r1.pdf) would let any rider enumerate other riders' receipts.",
      "unresolved_fact": "Does the calling route verify the receipt belongs to the session's rider before calling receipt()?"
    },
    {
      "id": "NV2", "status": "needs_validation",
      "location": "downloads.py _inside() then open()",
      "suspicion": "Symlink swap between realpath check and open.",
      "unresolved_fact": "Can any lower-trust process write into DOCS/maps?"
    }
  ],
  "refuted": [
    {"id": "R1", "candidate": "_inside bypass via sibling-prefix folder (maps2)", "evidence": "check is startswith(base + os.sep), not startswith(base)"},
    {"id": "R2", "candidate": "_inside bypass via absolute name, '..', or symlink", "evidence": "realpath resolves '..' and symlinks; os.path.join yields the absolute path, which then fails the prefix check"},
    {"id": "R3", "candidate": "empty name or '.' returns the folder", "evidence": "real == base does not start with base + os.sep, so it is rejected"}
  ]
}
```