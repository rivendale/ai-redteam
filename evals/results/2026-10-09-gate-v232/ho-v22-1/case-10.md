**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools were available in this session. I traced the code by reading it and ran nothing.

VERDICT: **SHIP WITH FIXES**. The loader does what was asked. It parses data, never code, and fails closed. The open items are hardening of Medium severity and below. The two facts that need checking before the first run are listed under NEEDS VALIDATION.

CONFIDENCE: **medium**. Three things limit it: this is a same-context review, I could not recompute the pinned SHA-256 or run the 4 tests, and the caller in the rebalancing job was not supplied.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `demand-2026-09.json`, `forecast.py`, `models.lock`, `test_forecast.py`.
- Not seen: the rebalancing job that calls `load_model`. **It matters.** How the job builds `path` and what it does when `ValueError` or `KeyError` is raised decides whether a refused model stops the job or gets bypassed.
- Not seen: the ops server's Python version and checkout settings. These matter a little, because of line-ending conversion and the hash.
- Not seen: test run output. "4 tests pass" is an assertion only.

COVERAGE:
- Checked: `forecast.py` (`LOCK`, `pinned`, `load_model`, `predict`), `test_forecast.py` (all 4 tests, with a mutation analysis on paper), `models.lock` (format), `demand-2026-09.json` (structure: 24 hourly entries, `base` = 10).
- Not checked: whether the SHA-256 digest matches the file, which needs computation; the calling job; actual test execution.

SEATS AND GATE: Only the local same-context reviewer ran. No subagent or external seat was available. Sensitivity gate: the work contains no credentials or personal data. The context *mentions* that the server holds fleet DB credentials and a dock API key, but neither appears in the work, so the gate passed.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | `forecast.py:10-11` (`file_name, digest = line.split()`) | Any lock line that is not exactly two tokens crashes `pinned`. This includes a blank line, a `# comment` line, or a line with a trailing extra field. The crash raises `ValueError: not enough values to unpack`, which is the **same exception type** as a hash mismatch. | Someone adds a second model to `models.lock` and leaves a blank line or a comment. Every load then fails, and the error looks like tampering ("does not match"-class `ValueError`), which misdirects whoever is on call. It fails closed, so nothing is corrupted. | Skip blank and `#` lines. Raise a distinct error (for example `LockFormatError`) that names the line number. Repro: write a lock containing `"\ndemand-2026-09.json <digest>\n"` and call `load_model(MODEL, lock=that)`. Expected: the model loads. Observed: `ValueError` on the blank line. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED (traced) | B | `forecast.py:21` (`return json.loads(raw)`), `:25` | Nothing checks the model's shape after the hash check. A pinned model with fewer than 24 `per_hour` entries, or a missing `base`, or a non-dict top level, loads without error and then fails in `predict` only at certain hours. | A future model is pinned with 23 entries. The job runs fine until hour 23, then raises `IndexError` mid-rebalance. The current file has 24 entries and `base` = 10, so it is unaffected. | After loading, assert `isinstance(m, dict)`, `len(m["per_hour"]) == 24`, and numeric values. Repro: pin a model whose `per_hour` has 23 entries, then call `predict(m, 23)` and observe `IndexError`. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED (traced) | B | `forecast.py:19-20` | The whole file is read and hashed **before** the lock lookup. An unlisted name is therefore read fully into memory before `KeyError` is raised. | The caller passes a large or unexpected file, for example a misconfigured path to a data dump. Memory spikes before the refusal. | Call `pinned(os.path.basename(path), lock)` first, then read and hash the file. Repro: point `load_model` at a large file named `x.json` and observe a full read before `KeyError`. | a✓ b✓ c✗ d✗ |
| F4 | Low | CONFIRMED (traced) | B | `forecast.py:10`, `:19`; `test_forecast.py:20` | Files are opened without `with`. Closing them depends on CPython's reference counting. In the test, the appended byte is flushed only when the file is garbage-collected. | Under PyPy, or with warnings turned into errors, you get `ResourceWarning`. On PyPy, test 2 could hash an unflushed copy. | Use `with open(...)` everywhere. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION
- **S1: does the pinned digest match the shipped file?** The unresolved fact is the output of `sha256sum demand-2026-09.json` on the ops server checkout, compared with `3fd1600a…e882`. If git converts line endings (`core.autocrlf`, `.gitattributes`), the digest differs and every run fails closed.
- **S2: how the caller handles the refusal.** The unresolved fact is whether the rebalancing job catches `ValueError` or `KeyError` from `load_model` and falls back to something unpinned, such as `demand-latest.json` or a direct `json.load`. If it does, the pin is decorative.
- **S3: do the "4 tests pass" on the target Python?** The unresolved fact is the actual run output on the ops server. On paper the tests are meaningful: deleting the hash comparison should turn test 2 red; making `pinned` return `None` instead of raising should turn test 3 red, because it raises `ValueError` rather than `KeyError`; removing `% 24` should turn test 4 red with `IndexError`. None of these mutations were executed.

## REFUTED
- **"Loading the model can execute code on a server holding credentials."** Refuted: the loader uses only `json.loads`, with no `pickle`, `eval` or `import`. A malicious file can at worst produce bad forecasts.
- **"TOCTOU between the hash check and the parse."** Refuted: the same `raw` bytes are hashed and then parsed (`forecast.py:19-21`). The file is never re-read.
- **"Path tricks bypass the pin via basename."** Refuted: the basename only selects which digest to compare against. A same-named file anywhere with different content still fails the content hash.
- **"The lock sits in the same repo, so the pin is worthless."** Refuted as a defect: anyone who can edit the lock can also edit `forecast.py`. The pin's real job is to stop an unreviewed or wrong model file from loading, and it does that. `LOCK` is resolved from the module's own location, not the working directory (`forecast.py:5`).

## WHAT HOLDS UP
- The module fails closed on unknown names (`KeyError`) and on modified content (`ValueError`).
- It parses data only, so there is no deserialization risk.
- The lock path does not depend on the working directory.
- `predict` handles hour wraparound and negative hours correctly, since Python's `-1 % 24 == 23`.
- The tests target the two security-relevant refusals rather than only the happy path.
- The shipped model has the 24 hourly entries `predict` needs.

## UNVERIFIED CLAIMS
- "The model file must match the hash pinned for its name." The logic does this, but the digest itself is unchecked. Confirm with S1.
- "4 tests pass." Confirm with S3.

## QUESTIONS FOR THE AUTHOR
1. What does the rebalancing job do when `load_model` raises?
2. Is the repository checked out on the ops server with line-ending conversion disabled for `*.json`?

## DECISION-MAKER SUMMARY
The loader is safe: it cannot run code and refuses any unpinned or altered model. Before the first run, confirm the digest on the server checkout (S1) and that the job does not fall back to an unpinned model when the loader raises (S2). If you proceed anyway, the risk is a job that fails to start, or one that silently ignores the pin if the caller swallows the error; there is no credential exposure from this module.

## OWNER SUMMARY
The code that loads the demand forecast is sound: it only accepts the exact approved forecast file and cannot be used to run anything on the server. Two quick checks remain before the first run: that the approved file on the server is byte-for-byte the one that was approved, and that the job stops rather than carries on if the file is refused. A few small tidy-ups would give clearer error messages and catch badly shaped future forecast files earlier.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "rebalancing job caller of load_model", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": true},
    {"item": "ops server git checkout settings (autocrlf/.gitattributes)", "status": "not_seen", "matters": true},
    {"item": "forecast.py", "status": "seen", "matters": true},
    {"item": "test_forecast.py", "status": "seen", "matters": true},
    {"item": "models.lock", "status": "seen", "matters": true},
    {"item": "demand-2026-09.json", "status": "seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work contains no credentials or personal data; context only mentions credentials exist on the server."},
  "coverage": {
    "checked": [
      {"unit": "forecast.py", "kind": "file"},
      {"unit": "forecast.py:pinned", "kind": "function"},
      {"unit": "forecast.py:load_model", "kind": "function"},
      {"unit": "forecast.py:predict", "kind": "function"},
      {"unit": "test_forecast.py", "kind": "file"},
      {"unit": "models.lock", "kind": "config"},
      {"unit": "demand-2026-09.json", "kind": "data"}
    ],
    "not_checked": [
      {"unit": "models.lock digest vs demand-2026-09.json bytes", "reason": "no tools to compute SHA-256"},
      {"unit": "test execution", "reason": "no tools"},
      {"unit": "rebalancing job caller", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "forecast.py:10-11",
     "scenario": "A blank or comment line added to models.lock makes line.split() unpack fail with ValueError, the same type as a hash mismatch, so every load fails and the error looks like tampering.",
     "fix": "Skip blank and # lines; raise a distinct LockFormatError naming the line.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Lock containing '\\ndemand-2026-09.json <digest>\\n'; call load_model(MODEL, lock=that). Expected: model loads. Observed: ValueError."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "forecast.py:21,25",
     "scenario": "A future pinned model with 23 per_hour entries loads, then predict raises IndexError at hour 23 mid-rebalance.",
     "fix": "Validate dict shape, 24 numeric per_hour entries and numeric base after loading.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Pin a model with 23 per_hour entries; predict(m, 23) raises IndexError."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "forecast.py:19-20",
     "scenario": "An unlisted large file is fully read and hashed before KeyError is raised, spiking memory.",
     "fix": "Look up the pinned digest before reading the file.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "load_model on a large file named x.json; observe full read before KeyError."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "forecast.py:10,19; test_forecast.py:20",
     "scenario": "Files opened without a context manager; on PyPy the test's appended byte may be unflushed when hashed, and ResourceWarnings appear.",
     "fix": "Use with open(...) everywhere.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Run the tests with python -W error::ResourceWarning; observe the warning raised as an error."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "models.lock:1",
     "suspicion": "The pinned digest may not match the file as checked out on the ops server.",
     "unresolved_fact": "Output of sha256sum demand-2026-09.json on the ops server checkout, compared with 3fd1600a...e882."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "caller of forecast.load_model (not supplied)",
     "suspicion": "The job may catch the refusal and fall back to an unpinned model.",
     "unresolved_fact": "Whether the rebalancing job catches ValueError/KeyError from load_model and loads a model without the pin."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "test_forecast.py",
     "suspicion": "The claim that 4 tests pass is unverified.",
     "unresolved_fact": "Actual run output of the 4 tests on the ops server's Python version."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Loading the model can execute code.", "evidence": "Only json.loads is used (forecast.py:21); no pickle, eval or import."},
    {"id": "R2", "candidate": "TOCTOU between the hash check and the parse.", "evidence": "The same raw bytes are hashed and parsed (forecast.py:19-21); the file is not re-read."},
    {"id": "R3", "candidate": "Basename lookup allows path-based bypass.", "evidence": "Basename only selects the digest; the content hash must still match."},
    {"id": "R4", "candidate": "A lock in the same repo makes the pin worthless.", "evidence": "Anyone able to edit the lock can edit forecast.py; the pin's purpose is stopping unreviewed files, which it does. LOCK resolves from __file__, not the working directory."}
  ]
}
```