**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no tools and no subagent, so this is a static read of `downloads.py` only. Nothing was executed.

VERDICT: **REWORK.** `receipt()` and `manual()` join an untrusted name straight onto the docs path, so any caller can read any file the server process can read. The containment guard `_inside()` exists but is applied only to `station_map()`.

CONFIDENCE: **medium.** The two path-traversal findings rest on documented `os.path.join` and `os.path.realpath` behaviour and are high-confidence. Confidence is limited by:
- a same-context, tool-less review;
- the HTTP layer that calls these functions was not supplied;
- no tests exist.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `downloads.py` (all 33 lines).
- Not seen: the web routing or handler layer that calls these functions (matters: it decides authentication, error-to-status mapping and response headers).
- Not seen: the directory layout under and around `/srv/pedalo/docs` (matters little: the traversal holds regardless of layout).
- Not seen: the deployment value of `PEDALO_DOCS` (minor).
- Not seen: any tests (none exist per `context.md`).

COVERAGE:
- Checked: `downloads.py:DOCS`, `_inside`, `receipt`, `manual`, `station_map`. Each was traced on the main path plus hostile inputs: `..` segments, absolute path, empty string, sibling-prefix folder, symlink, NUL byte, directory name.
- Not checked: the caller and routing layer, authentication and authorization, the filesystem layout, runtime behaviour.

SEATS AND GATE: Only a local same-context reviewer ran. No subagent was available, and no cross-vendor seats were requested at standard depth. Sensitivity gate passed: the code contains no personal data or secrets. Note that receipts served at runtime likely do contain personal data, which raises the stakes of F1.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | `downloads.py:18-21` `receipt()` | `os.path.join(DOCS, "receipts", name)` with no containment check. `..` segments escape the folder. An absolute `name` makes `join` discard the base entirely. | A request with `name='/etc/passwd'` opens `/etc/passwd`. A request with `name='../../<server file>'` reads files beside the docs directory, which `context.md` says holds other server files (config, secrets). This is arbitrary file read as the server user. | Use `open(_inside("receipts", name), "rb")`. **Repro:** call `receipt('/etc/passwd')`. Expected: `ValueError`. Observed by trace: the file's bytes are returned. Test: `pytest.raises(ValueError, receipt, '/etc/passwd')` and the same for `'../x'`. | y/y/y/y |
| F2 | Critical | CONFIRMED (traced) | B | `downloads.py:24-27` `manual()` | Same defect as F1 on the `manuals` folder. | `manual('../../<server file>')` or `manual('/etc/passwd')` returns that file. | Use `open(_inside("manuals", name), "rb")`. **Repro and test:** same as F1 with `manual`. | y/y/y/y |
| F3 | Medium | CONFIRMED | B | whole module (no tests) | The only security boundary in the module has no test. The guard's omission from two of three handlers is exactly the defect a test per handler would have caught. | A future refactor drops or weakens `_inside`, or a fourth handler skips it, and nothing goes red. | Add a parametrized test over all three handlers with these inputs: `'../x'`, `'/etc/passwd'`, `''`, `'..'`, a name starting with `'maps2/'`, and a symlink out of the folder (all must raise). Add a valid name (must return bytes) as the positive control. **Mutation check:** replace the `_inside` body with `return os.path.join(DOCS, folder, name)` and confirm the tests fail. | y/y/n/y |
| F4 | Low | PROBABLE | B | `downloads.py:30-32`, and `18-27` once fixed | A name that resolves to a sub-directory (e.g. `station_map('sub')`) passes `_inside` and then raises `IsADirectoryError`. Missing files raise `FileNotFoundError`. Neither is translated to a not-found error. | If the caller doesn't map these exceptions, the user gets a 500. In debug mode this could include a stack trace exposing absolute server paths. | In `_inside`, also require `os.path.isfile(real)`. Have the caller map `ValueError` and `OSError` to 404. **Repro:** create `maps/sub/`, call `station_map('sub')`, observe `IsADirectoryError`. | y/n/n/n |

## Needs validation

- **S1 (receipt authorization).** Receipts belong to individual riders, and the example name `2026-09-r1.pdf` looks sequential and guessable. Nothing in this module ties a receipt to the requesting rider. **Unresolved fact:** does the caller layer (not supplied) restrict `receipt()` to the authenticated rider's own files? If not, any rider can enumerate other riders' receipts, which is a personal-data exposure.
- **S2 ("handlers" requirement fit).** The request asks for download handlers. The work supplies plain file-reading functions with no routing, `Content-Type` or `Content-Disposition`. **Unresolved fact:** does existing routing code wrap these functions, so that "handler" here means the backing function?
- **S3 (TOCTOU between `realpath` and `open`).** Someone with write access inside `maps/` could swap a path component for a symlink after the check and before the open. **Unresolved fact:** can anyone other than deploy tooling write to the docs folders? If not, this is moot.

## Refuted

- **R1** "`_inside` can be bypassed by a sibling folder sharing the prefix (e.g. `maps2`)." It cannot: the check is `startswith(base + os.sep)`, not `startswith(base)` (`downloads.py:12`).
- **R2** "An absolute name bypasses `_inside`." It does not: `join` returns the absolute path, `realpath` resolves it outside `base`, and the function raises.
- **R3** "An empty name returns the folder itself." It does not: `realpath(base + '/')` equals `base`, which doesn't start with `base + os.sep`, so the function raises.
- **R4** "A symlink inside `maps/` leaks outside files." It does not: `realpath` follows the link before the check, so the function raises. That may be stricter than intended, but it is safe.
- **R5** "A NUL byte truncates the path." It does not: Python's `open` raises `ValueError: embedded null byte`.

## What holds up

- `_inside` is a correct realpath-plus-separator containment check. It survived `..`, absolute paths, empty names, prefix siblings, symlinks and NUL bytes.
- `station_map` is safe for file-read purposes.
- Files are opened in binary mode and closed by `with`.
- The `DOCS` environment-variable override is reasonable.

## Unverified claims

- The docstring of `_inside` says it "refuses any name that resolves outside". This is true by static trace but has never been run. A test with the F3 inputs would confirm it.
- The examples in the docstrings (e.g. `receipt('2026-09-r1.pdf')`) are illustrative and were not exercised.

## Questions for the author

1. What calls these functions, and does it enforce that a rider can fetch only their own receipts (S1)?
2. Was leaving out `_inside` in `receipt` and `manual` intentional? If so, why? (I can't see a valid reason.)

## Decision-maker summary

Do not deploy: two of the three download endpoints let anyone read arbitrary server files, including the configuration that sits beside the docs directory. The fix is two one-line changes plus a short test, using a guard the author already wrote. Also confirm that receipts are restricted to their owner before launch.

## Owner summary

Two of the three new download features can be tricked into handing out any file on the server, not just the documents they are meant to serve. The protection that prevents this was written but only switched on for station maps. It is a small fix, but it must be made and tested before the site goes live.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "downloads.py", "status": "seen", "matters": true},
    {"item": "caller/routing layer for the download handlers", "status": "not_seen", "matters": true},
    {"item": "filesystem layout around /srv/pedalo/docs", "status": "not_seen", "matters": false},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code contains no personal data or secrets; served receipts likely do at runtime."},
  "coverage": {
    "checked": [
      {"unit": "downloads.py", "kind": "file"},
      {"unit": "downloads.py:_inside", "kind": "function"},
      {"unit": "downloads.py:receipt", "kind": "function"},
      {"unit": "downloads.py:manual", "kind": "function"},
      {"unit": "downloads.py:station_map", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "caller/routing layer", "reason": "not supplied"},
      {"unit": "runtime behaviour", "reason": "no tools in this session; static trace only"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py:18-21",
     "scenario": "receipt('/etc/passwd') or receipt('../../<server file>') returns that file: os.path.join keeps '..' segments and discards the base when name is absolute, giving arbitrary file read as the server user.",
     "fix": "Open _inside('receipts', name) instead of os.path.join(DOCS, 'receipts', name).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Call receipt('/etc/passwd'); expect ValueError, observe (by trace) the file contents."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py:24-27",
     "scenario": "manual('/etc/passwd') or manual('../../<server file>') returns that file, the same traversal as F1.",
     "fix": "Open _inside('manuals', name) instead of os.path.join(DOCS, 'manuals', name).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Call manual('/etc/passwd'); expect ValueError, observe (by trace) the file contents."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py (no tests)",
     "scenario": "A refactor removes or weakens the _inside call on any handler and no test fails, re-opening file read.",
     "fix": "Parametrized test over all three handlers: '../x', '/etc/passwd', '', '..', a 'maps2/' prefix name and an outward symlink must raise; a valid name must return bytes. Mutate _inside to a plain join and confirm the test goes red.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Run the new test against the current receipt/manual; it fails on '/etc/passwd'."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "downloads.py:30-32",
     "scenario": "station_map('sub') where maps/sub is a directory passes _inside and then raises IsADirectoryError; missing files raise FileNotFoundError. If the caller doesn't map these, the user gets a 500, possibly with a path-leaking trace.",
     "fix": "Require os.path.isfile(real) in _inside; have the caller map ValueError and OSError to 404.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "mkdir maps/sub; call station_map('sub'); observe IsADirectoryError instead of a not-found error."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "downloads.py:18-21",
     "suspicion": "Any rider can fetch another rider's receipt by guessing its sequential name.",
     "unresolved_fact": "Whether the unsupplied caller restricts receipt() to the authenticated rider's own files."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "downloads.py (module)",
     "suspicion": "The request asked for download handlers; the work provides bare file readers with no routing or response headers.",
     "unresolved_fact": "Whether existing routing code wraps these functions as the handlers."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "downloads.py:10-14",
     "suspicion": "A symlink swap between realpath and open could escape the folder.",
     "unresolved_fact": "Whether any non-deploy principal can write inside the docs folders."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "A sibling prefix folder (maps2) bypasses _inside.", "evidence": "The check is startswith(base + os.sep) at downloads.py:12."},
    {"id": "R2", "candidate": "An absolute name bypasses _inside.", "evidence": "realpath resolves it outside base and the function raises ValueError."},
    {"id": "R3", "candidate": "An empty name returns the folder.", "evidence": "realpath gives base, which lacks the trailing separator, so the function raises."},
    {"id": "R4", "candidate": "A symlink in maps/ leaks outside files.", "evidence": "realpath follows the link before the containment check."},
    {"id": "R5", "candidate": "A NUL byte truncates the path.", "evidence": "Python open() raises ValueError on an embedded null byte."}
  ]
}
```

I could not run `tools/validate_findings.py` on this block (no tools this session). Run it before relying on the JSON.