# Redteam review: Pedalo download handlers

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so nothing was executed. Every result below comes from reading and tracing the code.

**VERDICT: SHIP WITH FIXES.** The path containment check holds against every escape I traced, and nothing confirmed is High or Critical. Two things should happen before production: confirm who is allowed to fetch receipts, and harden the traversal test.

**CONFIDENCE: medium.** It is limited by:
- a same-context review,
- no ability to run the tests or mutations,
- no view of the HTTP layer that calls these functions.

## INPUTS LEDGER

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | yes |
| context.md | seen | yes |
| downloads.py | seen in full | yes |
| test_downloads.py | seen in full | yes |
| The web layer / route wiring that calls `receipt` / `manual` / `station_map` | **not seen** | **Yes.** Rider authorization for receipts and mapping exceptions to HTTP responses happen there. |
| "2 tests pass" (context.md) | not seen run | Low. By reading, both tests should pass. |
| Deployment layout of `/srv/pedalo/docs` and `PEDALO_DOCS` | not seen | Low |

## COVERAGE

- **Checked:**
  - `downloads.py`: `_inside`, `receipt`, `manual`, `station_map`, and the `DOCS` config.
  - `test_downloads.py`: `setUp` and both tests.
  - The request's requirement fit.
- **Not checked:**
  - The caller and router (not supplied).
  - Runtime Python version behavior. This affects null-byte handling only, and both paths raise.
  - Filesystem permissions on the docs tree.

## SEATS AND GATE

- **Seats:** Only the local same-context reviewer ran. No cross-vendor seats were requested, and depth is standard.
- **Gate:** Not sensitive. The work is code with no personal data or credentials. The receipts it serves may hold personal data, and that drives NV1 below.

## Pass 1: Reconstruct

The work adds three handlers. Each joins a request-supplied name onto a fixed subfolder of `DOCS` and returns the file's bytes. `_inside` resolves both the folder and the target with `realpath`. It refuses any target that is not strictly below `base + os.sep`.

For the work to be correct, three things must hold:
1. `realpath` must fully resolve `..`, absolute paths and symlinks.
2. The prefix check must not be fooled by sibling folders.
3. The caller must handle exceptions and authorization.

The unstated assumption is that any requester may fetch any file in a folder, receipts included. This is Track B.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED (case is absent); PROBABLE (the mutation survives) | B | test_downloads.py:21-24 | The only traversal case is `../secret.txt`. Nothing covers a sibling-prefix escape, an absolute path, or a symlink escape. | Someone later "simplifies" line 11 to `startswith(base)`, or swaps `realpath` for `abspath`. A sibling `receipts_old/` dir or a symlink in `receipts/` then becomes readable, and CI stays green. | Add three cases: `fn("/etc/passwd")`; `fn("../receipts_x/f")` with `DOCS/receipts_x/f` created; and a symlink `receipts/l -> ../secret.txt`, then `receipt("l")`. **Mutations to confirm the gap:** (1) change `base + os.sep` to `base`; the current tests should stay green and the new sibling test should go red. (2) Replace `realpath` with `abspath`; the new symlink test should go red. | a✔ b✘ c✘ d✘ |
| F2 | Low | CONFIRMED | B | downloads.py:18,24,30 | Only an escape raises `ValueError`. A missing file raises `FileNotFoundError`, a directory name such as `"."` resolved to a subdir raises `IsADirectoryError`, and a null byte raises `ValueError` from a different source. | A generic caller maps unhandled exceptions to 500 with traceback, or to distinct status codes. That leaks server paths or lets callers probe which names exist. | Catch `OSError` in one place and map both "outside" and "not a regular file" to a single not-found response. Use `os.path.isfile(real)` in `_inside`. **Reproduction:** with a `receipts/sub/` directory, `receipt("sub")` raises `IsADirectoryError`, where a uniform refusal is expected. | a✔ b✔ c✘ d✘ |
| F3 | Low | CONFIRMED | B | test_downloads.py:9,14 | `setUp` overwrites the module global `downloads.DOCS` and never restores it. It also never removes its temp dirs. | Any later test in the same process that expects the real `DOCS` reads a deleted or foreign temp dir. Temp dirs also accumulate on CI. | Save and restore in `tearDown` (or use `unittest.mock.patch.object(downloads, "DOCS", ...)`), and `shutil.rmtree(self.tmp)`. | a✔ b✔ c✘ d✘ |

## NEEDS VALIDATION (no severity)

- **NV1: receipt ownership.** `receipt(name)` returns any file in `receipts/` to anyone. The example name `2026-09-r1.pdf` looks enumerable. If the caller does not check that the requesting rider owns that receipt, any rider can download other riders' receipts, which is a personal-data exposure.
  - **Settles it:** whether the route checks ownership before calling `receipt`. The request did not ask for auth, so this is a question about the deployment, not drift.
- **NV2: check-then-open race.** Between `realpath` (downloads.py:10) and `open` (downloads.py:18), a symlink swap inside a docs folder could redirect the open.
  - **Settles it:** whether any untrusted party can write into `docs/*`. If no one can, this is moot.
- **NV3: memory use.** `f.read()` loads whole files into memory.
  - **Settles it:** the maximum file size in `manuals/` and `maps/`, and the concurrency at peak.

## REFUTED

| Candidate | Evidence |
|---|---|
| Absolute name escapes (`/etc/passwd`) | `os.path.join(base, "/etc/passwd")` yields `/etc/passwd`, which fails the prefix check at line 11. |
| `..` traversal escapes | `realpath` normalizes it, and the existing test covers it. |
| Sibling-prefix escape (`../receipts2/x`) | The comparison is against `base + os.sep`, so `DOCS/receipts2/...` does not match `DOCS/receipts/`. |
| Symlink inside a folder escapes | `realpath` resolves the link target before the check. |
| Empty name or `"."` returns the folder | `real == base`, which does not start with `base + os.sep`, so `ValueError` is raised. |
| Test override of `DOCS` is ineffective | `_inside` reads the global `DOCS` at call time (line 9), not at import. |
| `DOCS` itself is a symlink and breaks the check | `base` is also `realpath`-resolved, so both sides compare in resolved form. |

## WHAT HOLDS UP

- **Requirement fit is exact.** There are three handlers, each serving its own folder under docs, with nothing extra.
- **Containment is centralized.** It lives in one function, and all three handlers use it.
- **The resolution is correct.** `realpath` is applied on both sides, and the separator-anchored prefix check is the right construction.
- **The traversal test would fail if the check were deleted.** It passes `../secret.txt`, and that file exists outside the folder, so the test does guard the basic check.

## UNVERIFIED CLAIMS

- **"2 tests in test_downloads.py pass."** Confirm by running `python -m unittest test_downloads -v`. Also apply the F1 mutations in a scratch copy.

## QUESTIONS FOR THE AUTHOR

1. Does the route enforce that a rider can only fetch their own receipts (NV1)?
2. How does the caller turn `ValueError` and `OSError` into HTTP responses (F2)?
3. Can anything other than deploy tooling write into `docs/*` (NV2)?

## DECISION-MAKER SUMMARY

The folder-escape protection is sound, and no blocking defect was found in this code. Before production, confirm that the receipt route restricts riders to their own receipts, and add the three missing escape tests. If you proceed without the ownership check, any rider who guesses a receipt name may read another rider's receipt.

## OWNER SUMMARY

The new download feature correctly stops people from reaching files outside the folders it is meant to serve. One open question matters before launch: make sure riders can only download their own receipts, not other people's. A few small test and error-handling improvements are also recommended.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "downloads.py", "status": "seen", "matters": true},
    {"item": "test_downloads.py", "status": "seen", "matters": true},
    {"item": "web route / caller of the handlers", "status": "not_seen", "matters": true},
    {"item": "test run output ('2 tests pass')", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code only; no personal data or credentials in the work."},
  "coverage": {
    "checked": [
      {"unit": "downloads.py", "kind": "file"},
      {"unit": "downloads.py:_inside", "kind": "function"},
      {"unit": "downloads.py:receipt", "kind": "function"},
      {"unit": "downloads.py:manual", "kind": "function"},
      {"unit": "downloads.py:station_map", "kind": "function"},
      {"unit": "test_downloads.py", "kind": "file"},
      {"unit": "downloads.py:DOCS", "kind": "config"}
    ],
    "not_checked": [
      {"unit": "HTTP route / caller", "reason": "not supplied"},
      {"unit": "test execution and mutation runs", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "test_downloads.py:21-24",
     "scenario": "A later edit weakens line 11 to startswith(base) or swaps realpath for abspath; sibling-prefix or symlink escapes open up while the single ../secret.txt test stays green.",
     "fix": "Add tests for an absolute path, a sibling-prefix folder (../receipts_x/f) and a symlink escape.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "In a scratch copy change 'base + os.sep' to 'base' on downloads.py:11; the current tests stay green, and the new sibling-prefix test goes red."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py:18,24,30",
     "scenario": "Missing files or directory names raise FileNotFoundError/IsADirectoryError instead of a uniform refusal; a generic caller may leak paths in a 500 or let callers probe which names exist.",
     "fix": "In _inside require os.path.isfile(real); map outside/not-found/not-a-file to one not-found response.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Create receipts/sub/ and call receipt('sub'); observe IsADirectoryError, expected a uniform refusal."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_downloads.py:9,14",
     "scenario": "setUp overwrites downloads.DOCS and never restores it or deletes temp dirs; later tests in the same process see a stale DOCS.",
     "fix": "Use mock.patch.object(downloads, 'DOCS', tmp) and shutil.rmtree in tearDown.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "After the suite runs, downloads.DOCS still points at the last temp dir rather than /srv/pedalo/docs."},
    {"id": "NV1", "status": "needs_validation", "track": "B", "location": "downloads.py:16-19",
     "suspicion": "Any requester can fetch any rider's receipt by an enumerable name.",
     "unresolved_fact": "Whether the calling route checks receipt ownership before calling receipt()."},
    {"id": "NV2", "status": "needs_validation", "track": "B", "location": "downloads.py:10,18",
     "suspicion": "Symlink swap between realpath check and open.",
     "unresolved_fact": "Whether any untrusted party can write into docs/* folders."},
    {"id": "NV3", "status": "needs_validation", "track": "B", "location": "downloads.py:19,25,31",
     "suspicion": "Whole-file reads may exhaust memory under load.",
     "unresolved_fact": "Maximum file size in docs folders and peak concurrent downloads."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Absolute path name escapes the folder.", "evidence": "os.path.join discards base for an absolute name; /etc/passwd fails the prefix check at downloads.py:11."},
    {"id": "R2", "candidate": "Sibling folder sharing a prefix (receipts2) passes the check.", "evidence": "Check compares against base + os.sep, not base."},
    {"id": "R3", "candidate": "Symlink inside a folder escapes.", "evidence": "realpath resolves the link target before the check at downloads.py:10."},
    {"id": "R4", "candidate": "Empty name or '.' returns the folder itself.", "evidence": "real == base does not start with base + os.sep; ValueError is raised."},
    {"id": "R5", "candidate": "Tests' DOCS override has no effect.", "evidence": "_inside reads the module global DOCS at call time (downloads.py:9)."}
  ]
}
```