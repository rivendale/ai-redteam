**Same-context review with no tools.** No subagent was available, and I could not run code. Every result below comes from reading the source and tracing standard-library behaviour by hand. For anything high-stakes, re-run this in a fresh session that has a scratch sandbox.

VERDICT: **REWORK**. `receipt()` and `manual()` join a name from the request onto the docs path without any containment check, so a request can read files outside their folders, including the server files that sit beside `docs`.
CONFIDENCE: medium. The traversal is a plain trace of `os.path.join` and `open`. Confidence is limited because nothing was executed, no router or caller code was supplied, and there are no tests.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `downloads.py`.
- Not seen: the HTTP routes that call these functions, including how `name` is pulled from the request and decoded. This matters. It decides whether a `/` or `..` can reach the functions. However, the functions themselves have to be safe, because the request says the name comes from the request.
- Not seen: tests. None exist, according to the context.
- Not seen: the deployment layout of `PEDALO_DOCS`. This matters only for what a traversal can reach.

COVERAGE:
- Scope: the whole work (`downloads.py`).
- Checked: `_inside`, `receipt`, `manual`, `station_map`, the `DOCS` config line, `request.md`, `context.md`.
- Not checked: the router and callers (not supplied), tests (not supplied), and runtime behaviour (no tools).

SEATS AND GATE:
- Only a same-context self-review ran.
- No cross-vendor seats were used. The sensitivity gate passed: this is plain code with no personal data or secrets.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | `downloads.py:18` | `receipt()` opens `os.path.join(DOCS, "receipts", name)` without containment. A `..` segment walks out of the folder. An absolute name makes `join` discard `DOCS` entirely. | A caller passes `name="../../app/config.py"` or `name="/etc/passwd"`. The function returns that file's bytes, which can include server files next to `docs` (see context.md). | **Fix:** `open(_inside("receipts", name), "rb")`. **Repro (written, not executed):** in a throwaway dir with no network, set `PEDALO_DOCS=/tmp/t/docs` and create `/tmp/t/docs/receipts/` and `/tmp/t/secret.txt`. Run `python3 -I -c "import downloads; print(downloads.receipt('../../secret.txt'))"`. Expected: `ValueError`. Per `os.path.join` semantics, it will print the secret instead. Repeat with `receipt('/etc/hostname')`. | a✔ b✔ c✔ d✔ |
| F2 | Critical | CONFIRMED (traced) | B | `downloads.py:24` | `manual()` has the same unguarded join (sibling of F1). | `name="../../secrets.env"` or any absolute path returns arbitrary readable files. | **Fix:** `open(_inside("manuals", name), "rb")`. **Repro:** same as F1, using `downloads.manual('../../secret.txt')` and `manual('/etc/hostname')`. | a✔ b✔ c✔ d✔ |

**Security boundary (F1, F2):**
- Principal: an anonymous or any rider client.
- Input it controls: the file name in the request.
- Control that fails: no containment check (the `_inside` helper exists but is not called).
- Boundary crossed: from the docs subfolder to the server filesystem.
- Resource affected: any file the server process can read.

**Sibling search:** I checked every `open(` call in the file (three) and every path built from `name`. Two are unguarded (F1, F2). `station_map` uses `_inside`. Nothing else in the file touches the filesystem.

## NEEDS VALIDATION
- **S1 (`receipt`, line 16–19). Receipt ownership.** Receipts are per rider, and nothing checks that the requester owns the receipt. Guessable names such as `2026-09-r1.pdf` would expose other riders' receipts. To settle: does the route layer authorise by rider before calling `receipt()`? That code was not supplied. Note that the request did not ask for this check either.
- **S2 (all three handlers). Error leakage.** `FileNotFoundError`, `IsADirectoryError` and `ValueError` propagate unhandled. If the caller turns them into a 500 with the message, absolute server paths are disclosed. To settle: the caller's error handling, which was not supplied.
- **S3 (route layer). How much of F1/F2 is reachable over HTTP.** A path converter that rejects `/` would block multi-segment traversal but not a bare `..`. That alone gives only the docs root, not the parent. Absolute names would also be blocked. To settle: the route definitions and the URL decoding. This does not change the fix, because the functions must defend themselves.

## REFUTED
- **"`_inside` can be bypassed with a sibling-prefix folder (`maps2/…`)."** Refuted: line 11 compares against `base + os.sep`, so `/srv/pedalo/docs/maps2/x` does not match `/srv/pedalo/docs/maps/`.
- **"`station_map` accepts an absolute name."** Refuted: `join(base, "/etc/passwd")` gives `/etc/passwd`, which fails the prefix check.
- **"A symlink inside `maps` escapes."** Refuted for static links: `realpath` resolves the link before the check. A race that swaps in a symlink between the check and `open` requires write access to `maps`, which is outside the request's threat model.
- **"An empty name or `.` returns the folder."** Refuted: `real == base` fails the `base + os.sep` prefix test, so the function raises `ValueError`.

## WHAT HOLDS UP
- `_inside` (lines 7–13) is a sound containment check. It resolves both base and target with `realpath`, compares against a separator-terminated prefix, and rejects absolute names, `..`, symlink escapes and sibling-prefix folders.
- `station_map` is safe as written.
- All three handlers match the request's shape: one per folder, a name in, file bytes out.

## UNVERIFIED CLAIMS
- That the traversal works end to end over HTTP. To confirm, send a request with the route layer in a sandbox.
- That no test exists to guard the containment check. The context says none were supplied. After the fix, add tests for `../x`, `/etc/passwd`, `''` and a `maps2` sibling for each handler. Confirm the tests go red when the `_inside` call is removed.

## QUESTIONS FOR THE AUTHOR
1. Why does only `station_map` use `_inside`? Was leaving it out of `receipt` and `manual` intentional?
2. Does the route that calls `receipt()` check that the receipt belongs to the logged-in rider?

## DECISION-MAKER SUMMARY
Two of the three handlers (F1, F2) let a request read arbitrary server files. The fix is two one-line changes that reuse the existing `_inside` helper, plus traversal tests for each handler. Shipping as is exposes configuration and secrets stored beside `docs` to anyone who can reach the download endpoints.

## OWNER SUMMARY
The receipt and manual downloads can be tricked into handing out files from elsewhere on the server, including files that may hold passwords or settings. The map download already has the right safety check, and the same check needs to be applied to the other two before launch. It is also worth confirming that riders can only download their own receipts.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "downloads.py", "status": "seen", "matters": true},
    {"item": "HTTP route/caller code", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-self", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "downloads.py", "kind": "file"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "downloads.py:_inside", "kind": "function"},
      {"unit": "downloads.py:receipt", "kind": "function"},
      {"unit": "downloads.py:manual", "kind": "function"},
      {"unit": "downloads.py:station_map", "kind": "function"},
      {"unit": "downloads.py:DOCS", "kind": "config"}
    ],
    "not_checked": [
      {"unit": "HTTP route/caller code", "reason": "not_supplied"},
      {"unit": "tests", "reason": "not_supplied"},
      {"unit": "runtime behaviour", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py:18",
     "scenario": "A request with name '../../app/config.py' or '/etc/passwd' makes receipt() return a file outside DOCS/receipts, including server files beside docs.",
     "fix": "Use open(_inside('receipts', name), 'rb'); add traversal tests.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Not executed (no tools). In an isolated scratch dir: PEDALO_DOCS=/tmp/t/docs, mkdir /tmp/t/docs/receipts, create /tmp/t/secret.txt; python3 -I -c \"import downloads; print(downloads.receipt('../../secret.txt'))\". Expected ValueError; per os.path.join semantics the secret's bytes are returned. Repeat with receipt('/etc/hostname').",
     "security": true,
     "boundary": {"principal": "any client of the download endpoint", "input": "the file name in the request",
                  "control": "no containment check; _inside not called", "crossed": "docs/receipts to server filesystem",
                  "resource": "any file readable by the server process"},
     "siblings_searched": {"searched": "every open() call and every path built from name in downloads.py",
                           "found": "manual() at line 24 (F2); station_map uses _inside and is safe"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py:24",
     "scenario": "A request with name '../../secrets.env' or an absolute path makes manual() return a file outside DOCS/manuals.",
     "fix": "Use open(_inside('manuals', name), 'rb'); add traversal tests.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Not executed (no tools). Same scratch setup as F1 with mkdir /tmp/t/docs/manuals; python3 -I -c \"import downloads; print(downloads.manual('../../secret.txt'))\". Expected ValueError; secret's bytes returned instead. Repeat with manual('/etc/hostname').",
     "security": true,
     "boundary": {"principal": "any client of the download endpoint", "input": "the file name in the request",
                  "control": "no containment check; _inside not called", "crossed": "docs/manuals to server filesystem",
                  "resource": "any file readable by the server process"},
     "siblings_searched": {"searched": "every open() call and every path built from name in downloads.py",
                           "found": "receipt() at line 18 (F1); station_map uses _inside and is safe"}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "downloads.py:16-19",
     "suspicion": "Any requester may fetch another rider's receipt by guessing its name.",
     "unresolved_fact": "Whether the route calling receipt() authorises by rider (caller not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "downloads.py:18,24,30",
     "suspicion": "Unhandled FileNotFoundError/IsADirectoryError/ValueError may leak absolute paths in error responses.",
     "unresolved_fact": "The caller's exception handling (not supplied)."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "route layer (not supplied)",
     "suspicion": "Exploit reach of F1/F2 over HTTP depends on whether the router passes '/' and '..' in the name.",
     "unresolved_fact": "Route definitions and URL decoding for the three endpoints."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "_inside is bypassable via a sibling-prefix folder like maps2.",
     "evidence": "Line 11 compares against base + os.sep."},
    {"id": "C2", "candidate": "station_map accepts absolute names.",
     "evidence": "join(base, '/etc/passwd') yields '/etc/passwd', which fails the prefix check."},
    {"id": "C3", "candidate": "A symlink inside maps escapes the folder.",
     "evidence": "realpath resolves symlinks before the check; a swap race needs write access to maps."},
    {"id": "C4", "candidate": "An empty name or '.' returns the folder itself.",
     "evidence": "real == base fails startswith(base + os.sep), raising ValueError."}
  ]
}
```