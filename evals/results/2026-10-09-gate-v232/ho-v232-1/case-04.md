VERDICT: **SHIP**. The path guard in `_inside` is the correct resolve-then-contain pattern and covers all three handlers. Nothing confirmed blocks production, but one open question about receipts should be answered before release (see Questions).

CONFIDENCE: **medium**. No tools were available, so nothing was run and the "2 tests pass" claim is unverified. The calling web layer was not supplied. This is a single-reviewer pass with no subagent. The work was not written in this conversation, so the reviewer does not share the author's context.

**INPUTS LEDGER**
- Seen: `request.md`, `context.md`, `downloads.py`, `test_downloads.py`.
- Not seen:
  - The route or handler code that calls these functions. **This matters**: per-rider authorization for receipts, how `name` is decoded, and how exceptions become HTTP responses all live there.
  - The test run output. Low impact; the tests were read and traced instead.
  - The deployed `PEDALO_DOCS` value and the contents of the docs tree. Low impact; symlinks are already handled by `realpath`.

**COVERAGE**
- Scope: the whole work (two files).
- Checked:
  - `downloads.py`: `_inside`, `receipt`, `manual`, `station_map` and the `DOCS` config.
  - `test_downloads.py`: `setUp` and both tests.
  - `request.md` and `context.md`.
- Not checked:
  - The route layer (not supplied).
  - Byte-level scan for invisible or bidirectional characters (no tools; the text as rendered shows none).
  - Execution of the tests (no tools).

**SEATS AND GATE**
- Seats: one local reviewer only. No subagent or cross-vendor seats were available without tools.
- Sensitivity gate: the code holds no personal data, credentials or client material. The receipts it serves are personal data at runtime.

**FINDINGS**

None confirmed.

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| none | | | | | | | | |

**NEEDS VALIDATION** (no severity)
- **S1, receipts may lack per-rider authorization** (`downloads.py:18-21`). `receipt(name)` takes no rider identity, so this function cannot check ownership. The example name `2026-09-r1.pdf` looks enumerable. If the route passes the requested name straight through, any rider could fetch another rider's receipt, which is personal and payment data. *Unresolved fact:* does the calling route check that the requesting rider owns that receipt before calling `receipt()`? Note that the request did not ask for this check, so if it is missing, the gap is in the request as much as in the code.
- **S2, the tests under-cover the guard** (`test_downloads.py:21-24`). Only `../secret.txt` is tried. Tracing two mutations against the test suggests both leave it green:
  - (i) `real.startswith(base)`, dropping `+ os.sep`: the test name resolves to `tmp/secret.txt`, which does not start with `tmp/receipts`, so it is still refused.
  - (ii) `os.path.abspath` in place of `realpath`: the test uses no symlink, so nothing changes.
  
  *Unresolved fact:* do these mutations leave the suite green when actually run in a scratch copy? To settle it, add cases for a sibling folder (`../receipts2/x`), an absolute path (`/etc/passwd`) and a symlink inside `receipts/` that points out, then confirm each case fails under its mutation.
- **S3, error handling and possible path disclosure** (`downloads.py:19,25,31`). A missing file raises `FileNotFoundError`, a folder name such as `.` or `sub/` raises `ValueError` or `IsADirectoryError`, and these messages include the absolute server path. *Unresolved fact:* does the route layer map these to 404/400 without echoing the exception text?

**REFUTED**
- **C1, traversal via `../`.** `realpath(join(base, name))` resolves `..` before the containment check, so the escape is refused. The traversal test exercises this, and it would fail if the guard were removed.
- **C2, absolute-path name.** `os.path.join(base, "/etc/passwd")` yields `/etc/passwd`, which fails `startswith(base + os.sep)`.
- **C3, sibling-prefix bypass** (`receipts_old`). The `+ os.sep` in the check blocks it.
- **C4, symlink escape.** `realpath` resolves symlinks before the check, so a link pointing outside the folder is refused.
- **C5, empty name or `.`.** Both resolve to `base`, which does not start with `base + os.sep`, so both are refused.
- **C6, TOCTOU symlink swap between check and `open`.** This needs write access inside the docs folders, which a rider sending a name does not have. No boundary is crossed from the request side.
- **C7, URL-encoded traversal.** If the name arrives undecoded, it is a literal filename. If it arrives decoded, C1 applies.

**WHAT HOLDS UP**
- The containment check is correct and shared by all three handlers. No handler skips it.
- The work fits the request exactly: three handlers, each with its own folder, and nothing extra.
- `DOCS` is configurable through an environment variable with a sane default.

**UNVERIFIED CLAIMS**
- "2 tests in test_downloads.py pass": confirm by running `python -m unittest test_downloads` in a scratch copy.

**QUESTIONS FOR THE AUTHOR**
1. Where is receipt ownership enforced? If nowhere, should receipts be scoped per rider (for example `receipts/<rider_id>/`) before release?
2. How does the route turn `ValueError` and `OSError` into responses?

**DECISION-MAKER SUMMARY**
The path-traversal protection is sound, so the docs-beside-server-files risk named in the context is handled. Before release, confirm that a rider can only download their own receipts. Otherwise any rider who guesses a file name may read another rider's payment record.

**OWNER SUMMARY**
The new download code safely stops people from reaching files outside the three download folders. One thing still needs checking: whether riders can only download their own receipts, since the code itself does not check who is asking. Please confirm that before it goes live.

The two `needs_validation` entries below have no severity by design, so they do not carry the severity, scenario and fix fields the output note lists for findings.

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
    {"item": "route/caller code for the download handlers", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code only; receipts served at runtime are personal data, none present in the work."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "downloads.py", "kind": "file"},
      {"unit": "downloads.py:_inside", "kind": "function"},
      {"unit": "downloads.py:receipt", "kind": "function"},
      {"unit": "downloads.py:manual", "kind": "function"},
      {"unit": "downloads.py:station_map", "kind": "function"},
      {"unit": "downloads.py:DOCS", "kind": "config"},
      {"unit": "test_downloads.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "route/caller code", "reason": "not_supplied"},
      {"unit": "test execution and mutation runs", "reason": "no_tools"},
      {"unit": "byte-level hidden-character scan", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "downloads.py:18-21",
     "suspicion": "receipt(name) has no rider identity; with enumerable names any rider may fetch another rider's receipt.",
     "unresolved_fact": "Whether the calling route verifies the requesting rider owns the named receipt."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "test_downloads.py:21-24",
     "suspicion": "The traversal test likely stays green if '+ os.sep' is dropped or realpath is replaced by abspath.",
     "unresolved_fact": "Result of running those two mutations against the suite in a scratch copy."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "downloads.py:19,25,31",
     "suspicion": "FileNotFoundError/IsADirectoryError messages contain absolute server paths and may reach the client.",
     "unresolved_fact": "How the route layer maps exceptions to HTTP responses."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "'../' traversal escapes the folder.", "evidence": "realpath resolves '..' before startswith(base + os.sep); test covers it."},
    {"id": "C2", "candidate": "Absolute-path name escapes.", "evidence": "os.path.join discards base; result fails the containment check."},
    {"id": "C3", "candidate": "Sibling-prefix folder bypass.", "evidence": "Check uses base + os.sep."},
    {"id": "C4", "candidate": "Symlink inside the folder escapes.", "evidence": "realpath resolves symlinks before the check."},
    {"id": "C5", "candidate": "Empty name or '.' returns the folder.", "evidence": "Resolves to base, which fails startswith(base + os.sep)."},
    {"id": "C6", "candidate": "TOCTOU symlink swap.", "evidence": "Requires write access inside docs folders, not available to a requester."},
    {"id": "C7", "candidate": "URL-encoded traversal.", "evidence": "Undecoded is a literal filename; decoded is caught as C1."}
  ]
}
```