VERDICT: **REWORK.** Two of the three handlers, `receipt` and `manual`, read any file the server process can open. The path-confinement helper exists but only `station_map` calls it.

CONFIDENCE: **medium.** The core findings rest on the documented behaviour of `os.path.join`, which is deterministic, so I could trace them by hand. I had no tools, though: I ran nothing, and the request routing layer was not supplied. This is a single independent reviewer that did not author the work; no subagent or cross-vendor seats were available.

INPUTS LEDGER:
- **Seen:** request.md, context.md, downloads.py (the full module).
- **Not seen: the web framework, routes, or the code that passes the request's name into these functions.** This matters for the needs-validation items: how errors map to HTTP, and whether a rider can only fetch their own receipts. It does not change F1 or F2, because the module says "Names come from the request".
- **Not seen: tests.** context.md says none were supplied. This matters, because nothing guards the confinement check.
- **Not seen: the deployed value of `PEDALO_DOCS` and the directory layout.** This does not change the findings. Context confirms the docs directory sits beside other server files.

COVERAGE:
- **Checked:** `downloads.py`, including `DOCS`, `_inside`, `receipt`, `manual` and `station_map`, and the request fit of all three handlers.
- **Not checked:** routing and HTTP glue, auth and session handling, filesystem permissions and deployment. None were supplied.

SEATS AND GATE: one reviewer ran (Claude, this session, not the author's context). No cross-vendor seats were used, because depth was standard and the user did not ask for them. The sensitivity gate is not triggered: the work is code only and contains no personal data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | downloads.py:18-21 (`receipt`) | The file name taken from the request is joined to the path unchecked. `_inside` is never called. `os.path.join` keeps `..` segments, and if a component is absolute it throws away everything before it. | A request with `name="../../settings.py"` opens `/srv/pedalo/settings.py`. A request with `name="/etc/passwd"` opens `/etc/passwd`. The rider site returns server files and secrets that sit beside the docs directory. | Use `open(_inside("receipts", name), "rb")`. **Repro:** `downloads.DOCS=str(tmp/"docs")`; create `tmp/"secret.txt"`; call `receipt("../../secret.txt")`. Expected: `ValueError`. Observed: the secret's bytes are returned. | y/y/y/y |
| F2 | Critical | CONFIRMED | B | downloads.py:24-27 (`manual`) | Same defect as F1, in the manuals folder. | `manual("/etc/passwd")` or `manual("../../<config>")` returns arbitrary readable files. Manuals are a public, unauthenticated-looking endpoint, so they are the easiest route in. | Use `open(_inside("manuals", name), "rb")`. **Repro:** the same test as F1 against `manual`. | y/y/y/y |
| F3 | Medium | CONFIRMED | B | downloads.py (whole module; no tests) | No test exercises `_inside` or the traversal case. That is how two of the three handlers shipped without the guard. | A later edit adds a fourth handler, or refactors one, using a raw `os.path.join`. Nothing goes red. | Add one parametrized test over all three handlers. Inputs: `../../secret.txt`, `/etc/passwd` (absolute), `""`, and a sibling prefix such as `../maps2/x`. Each must raise. Confirm the test fails on the current `receipt`/`manual` before you fix them. | y/y/n/y |

## NEEDS VALIDATION

- **S1. Receipt ownership (IDOR).** Receipt names follow a guessable pattern (`2026-09-r1.pdf`). Nothing in this module ties a receipt to the requesting rider. The open question: does the route layer check that the receipt belongs to the logged-in rider before calling `receipt()`? If not, every rider can enumerate other riders' receipts, which contain personal and payment data. That would be at least High.
- **S2. Error mapping.** `_inside` raises `ValueError`, and `open` raises `FileNotFoundError` or `IsADirectoryError` (for example `name="."` after a fix, or a subfolder name). The open question: does the caller turn these into 400/404 responses, or do they surface as 500s with stack traces that include absolute paths?
- **S3. Symlink race.** `_inside` resolves the path and then `open` reopens it by path. If anyone untrusted can write into `docs/maps`, a symlink could be swapped in between the check and the open. The open question: who can write to the docs folders in production?

## REFUTED

- **R1: "`_inside` can be bypassed with a sibling-prefix folder (`maps2`)."** Refuted. The check is `startswith(base + os.sep)`, not `startswith(base)`, so `/…/maps2/x` fails against `/…/maps/`.
- **R2: "`_inside` accepts absolute names."** Refuted. `os.path.join(base, "/etc/passwd")` returns `/etc/passwd`, which does not start with `base + os.sep`, so `ValueError` is raised.
- **R3: "Symlinks inside `maps` pointing outside escape the check."** Refuted. Both `base` and the target go through `realpath` before the comparison.

## WHAT HOLDS UP

- `_inside` is a sound confinement check. It handles `..`, absolute names, symlinks, the sibling-prefix trick, and the empty or `.` name (which resolves to `base` itself and is rejected).
- `station_map` uses it correctly.
- All three handlers open files in binary mode, which is correct for PDFs and PNGs.
- Functionally, the module covers the three downloads that were asked for.

## UNVERIFIED CLAIMS

- The module docstring says "Names come from the request" (unverified because the routing was not supplied). Confirm by reading the route definitions.
- I did not execute the reproductions above. Running the F1/F2 test in a scratch copy settles them in seconds.

## QUESTIONS FOR THE AUTHOR

1. Why do `receipt` and `manual` bypass `_inside`? Was this intentional?
2. Does the route that serves receipts check that the receipt belongs to the logged-in rider?
3. What does the caller return to the client when these functions raise?

## DECISION-MAKER SUMMARY

Do not deploy. The receipt and manual downloads let anyone fetch arbitrary server files, including config beside the docs directory. The fix is two one-line changes plus a regression test. Before release, also confirm that riders can only download their own receipts.

## OWNER SUMMARY

Two of the three new download features let a visitor ask for any file on the server, not just the documents meant to be shared. The protection that blocks this already exists and works on the station-map download; it just needs to be switched on for the other two, and a check added so the problem cannot quietly come back. We should also confirm that each rider can only see their own receipts before this goes live.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "downloads.py", "status": "seen", "matters": true},
    {"item": "routing / HTTP layer calling downloads.py", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "production PEDALO_DOCS value and directory layout", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-single-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "downloads.py", "kind": "file"},
      {"unit": "downloads.py:DOCS", "kind": "config"},
      {"unit": "downloads.py:_inside", "kind": "function"},
      {"unit": "downloads.py:receipt", "kind": "function"},
      {"unit": "downloads.py:manual", "kind": "function"},
      {"unit": "downloads.py:station_map", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "routing / HTTP layer", "reason": "not supplied"},
      {"unit": "auth / session handling for receipts", "reason": "not supplied"},
      {"unit": "tests", "reason": "none supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py:18-21 (receipt)",
     "scenario": "A request with name='../../settings.py' or name='/etc/passwd' is passed to os.path.join without _inside; the handler returns arbitrary server files beside or outside the docs directory.",
     "fix": "Open _inside('receipts', name) instead of os.path.join(DOCS, 'receipts', name).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Set downloads.DOCS to tmp/docs, create tmp/secret.txt, call receipt('../../secret.txt'); expect ValueError, observe the secret's bytes."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py:24-27 (manual)",
     "scenario": "manual('/etc/passwd') or manual('../../<config>') returns arbitrary readable server files because _inside is not used.",
     "fix": "Open _inside('manuals', name) instead of os.path.join(DOCS, 'manuals', name).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Set downloads.DOCS to tmp/docs, create tmp/secret.txt, call manual('../../secret.txt'); expect ValueError, observe the secret's bytes."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py (no tests for _inside or traversal)",
     "scenario": "A future handler or refactor uses a raw os.path.join and no test fails, as already happened for receipt and manual.",
     "fix": "Add a parametrized test over all three handlers with '../../secret.txt', '/etc/passwd', '' and '../maps2/x', each expected to raise; confirm it fails on the current code first.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Run the proposed test against the current module; receipt and manual cases fail."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "downloads.py:18-21 (receipt) and its route",
     "suspicion": "Any rider may download another rider's receipt by guessing its name (IDOR).",
     "unresolved_fact": "Whether the route checks that the receipt belongs to the logged-in rider before calling receipt()."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "downloads.py:_inside and callers",
     "suspicion": "ValueError / FileNotFoundError / IsADirectoryError may surface as 500s exposing absolute paths.",
     "unresolved_fact": "How the calling route maps these exceptions to HTTP responses."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "downloads.py:_inside / station_map",
     "suspicion": "Check-then-open race allows a swapped symlink to escape the folder.",
     "unresolved_fact": "Whether any untrusted party can write into the docs folders in production."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "_inside bypassable via sibling-prefix folder such as maps2.",
     "evidence": "Comparison is startswith(base + os.sep), so /.../maps2/x does not match /.../maps/."},
    {"id": "R2", "candidate": "_inside accepts absolute names.",
     "evidence": "os.path.join(base, '/etc/passwd') yields '/etc/passwd', which fails the startswith check and raises ValueError."},
    {"id": "R3", "candidate": "Symlinks inside maps pointing outside escape the check.",
     "evidence": "Both base and target are passed through os.path.realpath before comparison."}
  ]
}
```