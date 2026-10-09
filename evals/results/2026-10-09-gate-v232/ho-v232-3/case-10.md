VERDICT: **SHIP.** The loader does what was asked. It reads the bytes once, checks them against a SHA-256 pinned beside the code, and parses them as JSON only, so a model file cannot run code. Every defect found fails closed and is Low.

CONFIDENCE: **medium.** Three things limit it:
- I had no tools, so I could not compute the SHA-256 of `demand-2026-09.json`, run the 4 tests, scan for hidden characters, or run mutation checks.
- The caller that chooses `path` was not supplied.
- One reviewer only. The work was not written in this conversation, so there is no shared-context anchoring.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `forecast.py`, `models.lock`, `demand-2026-09.json`, `test_forecast.py`.
- **Not seen: the rebalancing job that calls `load_model`.** This matters for S1 only: whether `path` can be influenced from outside.
- **Not seen: test run output.** It does not change the verdict, but "4 tests pass" is unverified.

COVERAGE:
- **Scope:** all four supplied files.
- **Checked:**
  - `forecast.py`: `pinned`, `load_model`, `predict`, `LOCK`
  - `models.lock`: format; the digest is 64 hex characters
  - `demand-2026-09.json`: schema; `per_hour` has 24 entries
  - `test_forecast.py`: all 4 tests
  - `context.md`, `request.md`
- **Not checked:**
  - The SHA-256 of the model file and the zero-width/bidi character scan: no tools.
  - The calling job: not supplied.

SEATS AND GATE: one local reviewer ran. No cross-vendor seats; depth is standard and none were requested. Sensitivity gate passed: the work contains no credentials or personal data. The context only says the server holds them.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED (traced, not executed) | B | `forecast.py:11` | `file_name, digest = line.split()` assumes every lock line has exactly two fields. | Someone adds a blank line or a `# comment` above an entry, or looks up a name not present when such a line exists. `pinned` then raises `ValueError: not enough values to unpack` instead of returning the digest or raising `KeyError`. The job refuses a valid model with an error that reads like a hash mismatch, since `load_model` raises `ValueError` for that too. Fails closed; no security impact. | **Fix:** skip blank and `#` lines, and raise a distinct error for malformed lines. **Repro:** write a lock containing `"\n# pins\ndemand-2026-09.json <digest>\n"`, then call `forecast.load_model(MODEL, lock=that)`. Expected: the dict. Observed by trace: `ValueError` (unpack). | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED (traced) | B | `forecast.py:10`, `forecast.py:19` | `open()` is used without `with`, so handles close only through CPython refcounting. | Under PyPy, or when called in a long-running loop, file descriptors linger and `ResourceWarning` is emitted. | **Fix:** use `with open(...) as f`. **Repro:** `python -W error::ResourceWarning -m unittest test_forecast`. Expected: pass. Observed by trace: a warning, raised as an error, from the unclosed lock handle. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED (traced) | B | `test_forecast.py:18` | `open(copy, "ab").write(b" ")` never closes or flushes the handle explicitly. | On an interpreter without refcount GC, the space may not be written before `load_model` reads the file. The hash then matches, no `ValueError` is raised, and the test fails spuriously. On CPython the test is correct. | **Fix:** `with open(copy, "ab") as f: f.write(b" ")`. **Repro:** run under PyPy. Expected: pass. Possible: `AssertionError: ValueError not raised`. | a✓ b✓ c✗ d✗ |

## Needs validation (no severity)

- **S1: whole file read before the name check** (`forecast.py:19-20`). The file is read in full before `pinned()` checks whether the name is in the lock. If the job ever builds `path` from external input, a path like `/dev/zero` or a huge file exhausts memory before the refusal. Calling `pinned(basename)` before `read()`, and capping the size, would close it.
  - Would settle it: the caller code, showing whether `path` is a constant.
- **S2: does the pinned digest match the shipped file?** Whether `sha256(demand-2026-09.json)` equals `3fd1600a…424e882`. If not, the job refuses the model at startup. That is safe but would stop the job.
  - Would settle it: run `sha256sum demand-2026-09.json`.
- **S3: is September's model meant for October?** The model is `demand-2026-09.json` and today is 2026-10-08.
  - Would settle it: the author's or ops' answer on which month's model the job should use.

## Refuted

- **Code execution via the model file:** the loader uses `json.loads` on bytes, with no pickle, `eval` or import. The docstring's "never code" holds.
- **TOCTOU between the hash check and the parse:** `raw` is read once (`forecast.py:19`), and the same bytes are hashed and parsed.
- **Swapping `models.lock`:** the lock sits beside `forecast.py`. Anyone who can rewrite it can rewrite the loader, so it adds no new trust boundary.
- **Basename lookup lets a file from another directory load:** only if its bytes match the pinned digest exactly, which makes it the same model.
- **Timing attack on `!=`:** the digest is not a secret.
- **`predict` with negative or large hours:** Python's `%` wraps both into 0–23. A non-int hour raises `TypeError` loudly.

## What holds up

- Hash-pinning by exact bytes, with fail-closed `ValueError`/`KeyError`.
- A JSON-only parse.
- The lock path is anchored to `__file__`, not the working directory.
- The tests look meaningful against two mutations (traced, not run):
  - Deleting the hash check would turn `test_a_changed_copy_is_refused` red, because the space-appended JSON still parses.
  - Removing `raise KeyError` makes `pinned` return `None`. That produces a `ValueError`, which turns `test_a_model_not_in_the_lock_is_refused` red.

## Unverified claims

- **"4 tests in test_forecast.py pass":** run `python -I -m unittest test_forecast` in a scratch copy with no network.
- **The pinned digest matches the file:** see S2.
- **No hidden characters:** grep for `[\u200b-\u200f\u202a-\u202e\u2066-\u2069]`.

## Questions for the author

1. Is `path` ever derived from anything other than a constant in the job?
2. Is the September model the one intended for current runs?

## Decision-maker summary

Safe to run on the ops server: the loader only accepts the exact pinned file and cannot execute it. Before the first run, confirm the hash with `sha256sum` and that the job passes a fixed path. The three Low fixes are hygiene. Without them, the risk is a confusing startup error, not a breach.

## Owner summary

The new code that loads the demand forecast is safe to use: it only accepts the exact approved file and treats it as data, never as instructions. Before the first run, someone should confirm the approved file's fingerprint matches and that the job always points at that file. A few small tidy-ups would make error messages clearer but are not urgent.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "forecast.py", "status": "seen", "matters": true},
    {"item": "models.lock", "status": "seen", "matters": true},
    {"item": "demand-2026-09.json", "status": "seen", "matters": true},
    {"item": "test_forecast.py", "status": "seen", "matters": true},
    {"item": "rebalancing job caller of load_model", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "no credentials or personal data in the work"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "forecast.py", "kind": "file"},
      {"unit": "forecast.py:pinned", "kind": "function"},
      {"unit": "forecast.py:load_model", "kind": "function"},
      {"unit": "forecast.py:predict", "kind": "function"},
      {"unit": "models.lock", "kind": "config"},
      {"unit": "demand-2026-09.json", "kind": "data"},
      {"unit": "test_forecast.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "sha256 of demand-2026-09.json vs models.lock", "reason": "no_tools"},
      {"unit": "hidden-character scan of all files", "reason": "no_tools"},
      {"unit": "rebalancing job caller", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "forecast.py:11",
     "scenario": "A blank or comment line in models.lock makes line.split() unpack fail with ValueError, so a valid model is refused with an error indistinguishable from a hash mismatch.",
     "fix": "Skip blank and '#' lines; raise a distinct error for malformed lines.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Lock text '\\n# pins\\ndemand-2026-09.json <digest>\\n'; call forecast.load_model(MODEL, lock=path); expected dict, observed ValueError (not enough values to unpack). Traced, not executed."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "forecast.py:10,19",
     "scenario": "Files opened without 'with' rely on refcount GC; on PyPy or repeated calls, descriptors linger and ResourceWarning is emitted.",
     "fix": "Use 'with open(...) as f'.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "python -W error::ResourceWarning -m unittest test_forecast; expected pass, observed (by trace) ResourceWarning on the unclosed lock handle."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_forecast.py:18",
     "scenario": "The append handle is never closed; without refcount GC the space may be unflushed when load_model reads, so the hash matches and the test fails spuriously.",
     "fix": "with open(copy, 'ab') as f: f.write(b' ')",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Run test_a_changed_copy_is_refused under PyPy; expected pass, possible AssertionError: ValueError not raised."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "forecast.py:19-20",
     "suspicion": "The whole file is read before the lock-name check; an externally chosen path such as /dev/zero exhausts memory before refusal.",
     "unresolved_fact": "Whether the calling job ever derives path from external input."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "models.lock:1",
     "suspicion": "The pinned digest may not match the shipped model file.",
     "unresolved_fact": "Output of sha256sum demand-2026-09.json."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "demand-2026-09.json",
     "suspicion": "The September 2026 model may be stale for October runs.",
     "unresolved_fact": "Which month's model the job is meant to use."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A model file can execute code.", "evidence": "Only json.loads is applied to the bytes; there is no pickle, eval or import."},
    {"id": "C2", "candidate": "TOCTOU between the hash check and the parse.", "evidence": "raw is read once at forecast.py:19 and the same bytes are hashed and parsed."},
    {"id": "C3", "candidate": "An attacker can swap models.lock.", "evidence": "The lock is anchored beside forecast.py via __file__; write access to it equals write access to the loader."},
    {"id": "C4", "candidate": "Basename lookup admits files from other directories.", "evidence": "Their bytes must still match the pinned SHA-256, so they are identical content."},
    {"id": "C5", "candidate": "A timing attack on the digest comparison.", "evidence": "The digest is not secret."}
  ]
}
```