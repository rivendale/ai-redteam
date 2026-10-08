**Review mode:** I'm not the author of this PR, so the review is independent in that sense. I had no tools, so nothing was executed. `config/limits.yaml`, commit 91c4e7a, and the callers of `ratelimit.py` were not provided. Every behavior claim below comes from reading the patch.

## Pass 1: Reconstruct

The PR claims that per-plan limits now come from `config/limits.yaml`, added in 91c4e7a, and that tests pass. It adds `load_limits()`, a hand-rolled line parser, and changes `allowed()` to use `limits.get(plan)`, which returns `True` (unlimited) when a plan has no entry. Load-bearing assumptions:

- the file is always present and readable at a CWD-relative path in every deployment;
- ops will only ever write flat `plan: integer` lines;
- some caller actually invokes `load_limits()` and drops the old in-code values;
- "change without a deploy" is met by whatever reload model the callers use;
- treating a missing file or missing plan as unlimited is acceptable for a backend these limits exist to protect. Nobody asked for this, and it is the most dangerous assumption.

## Pass 2 / 3: Findings

**VERDICT: REWORK.** The change converts every config failure mode (missing file, wrong CWD, typo'd or quoted key, renamed plan) into unlimited access to a shared production backend. The new loader also has no tests.

**CONFIDENCE IN VERDICT: medium-high.** The fail-open logic is visible in the diff. Confidence is limited by: no execution, no view of `config/limits.yaml` or 91c4e7a, and no view of the callers.

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `load_limits`: `except FileNotFoundError: pass` together with `allowed`: `if limit is None: return True` | Fail-open. A missing file yields `{}`, and every plan then becomes unlimited. The docstring presents this as intended ("means no limits are configured"). | The config is not shipped in an image, or a volume mount fails. Every request from every plan is then allowed and the shared backend is unprotected, with no error or log. | Fail closed. Raise on a missing or unreadable file at startup. In `allowed`, deny (or raise) for unknown plans. Add tests for the missing-file and unknown-plan cases. |
| 2 | Critical | CONFIRMED | `allowed`: `limits.get(plan)` → `True` | Unknown or mis-keyed plans become unlimited. Before the change, `limits[plan]` raised `KeyError` (fail loud). This semantic change was not requested and is not mentioned in PR.md. | Ops writes `Free: 100`, or a new plan `team` launches without a config entry. Those users get no limit. | Same fix as #1. Validate at load time that every known plan has a limit. |
| 3 | High | CONFIRMED | `LIMITS_PATH = "config/limits.yaml"` | The path is resolved relative to the process CWD, not to the module or an env/config setting. | The service is started by systemd, cron, or a container with a different workdir. The result is `FileNotFoundError`, which is swallowed (#1), so the service runs unlimited. | Resolve the path from an env var or an absolute path. Fail if it is not found. |
| 4 | High | CONFIRMED | parser loop: `plan, n = line.split(":", 1)`; `int(n)` | The file is named `.yaml`, but the code is not a YAML parser. Valid YAML that ops will plausibly write breaks it in two ways. Inline comments (`free: 100  # raised`), `1_000`, `100.0`, empty values, and any non-limit key such as `version: v2` raise an uncaught `ValueError`. Quoted keys (`"free": 100`) store the key as `"free"` with quotes, so the lookup misses and the plan becomes unlimited (#2). Nested YAML (`limits:\n  free: 100`) raises on `limits:`. | An ops edit with an inline comment crashes the load, or a quoted key silently removes a plan's limit. | Use `yaml.safe_load` with schema validation (dict of known plan → positive int), or rename the format to something that is not YAML and document it strictly. Reject unknown keys, non-positive values, and duplicates. |
| 5 | High | PROBABLE | patch as a whole; callers not shown | Nothing in the diff calls `load_limits()`. The old in-code limits must live in a caller that this PR does not touch, since base `ratelimit.py` already takes `limits` as a parameter. "Limits now come from config" is therefore not demonstrated by this PR. | Callers keep passing the hardcoded dict, so ops edits to the YAML have no effect. Or the old and new sources both exist and diverge. | Show the caller change. Remove the hardcoded dict. Add an integration test showing a value from the file reaches `allowed`. |
| 6 | Medium | UNVERIFIED | requirement "change them without a deploy" | There is no reload mechanism. If limits load once at startup, a change needs a restart. That may or may not count as a "deploy" for ops. | Ops edits the file in an emergency, sees nothing change, and escalates. | Confirm what "without a deploy" means. If needed, add a reload on SIGHUP or mtime that keeps the last good config when a parse fails. |
| 7 | Medium | CONFIRMED | `tests/test_ratelimit.py` | The tests cover only the pre-existing `<` comparison. There are zero tests of `load_limits`, the missing file, unknown plans, comments, or bad values. `"pro"` is defined but never asserted. "Tests pass" says nothing about the new code. | Each of #1–#4 ships green. | Add loader tests: valid file, comment line, inline comment, quoted key, bad int, missing file, unknown plan. |
| 8 | Medium | UNVERIFIED | PR.md: "the file and its values are added in commit 91c4e7a" | The config file and its values were not provided. It is unknown whether 91c4e7a is in this PR's range (head e07b3d8, base 5a1c2f6), whether the values match the old hardcoded ones, and whether every plan is present. | 91c4e7a is not an ancestor of e07b3d8, so the file is absent on merge and the service runs unlimited (#1). Or a value is mistyped (e.g. 10000 vs 1000). | Run `git merge-base --is-ancestor 91c4e7a e07b3d8`. Diff the YAML values against the removed constants. |
| 9 | Low | CONFIRMED | parser | Duplicate keys silently take the last value. Negative and zero limits are accepted. `open()` uses the locale encoding. | A duplicate `free:` line overrides the intended value unnoticed. | Validate during load. Use `encoding="utf-8"`. |

## What holds up

- The comparison `used_today < limit` is unchanged and correct for configured plans; the existing test exercises the boundary at 99/100.
- Full-line `#` comments and blank lines are skipped correctly.
- `split(":", 1)` and `int()` tolerate surrounding whitespace and newlines.
- Errors other than `FileNotFoundError` (permissions, directory) still propagate.

## Unverified claims

- **"Tests pass":** run `python -m unittest` at e07b3d8. This would not cover the new code anyway (#7).
- **The file and values are in 91c4e7a:** check ancestry and inspect the file contents.
- **Limits actually come from config:** inspect the call sites of `allowed` and `load_limits`.

## Questions for the author

1. Is fail-open on a missing file or unknown plan intentional? Who approved unlimited access as the default for a shared backend?
2. Where are the old hardcoded limits, and which caller now uses `load_limits()`?
3. Is 91c4e7a in this branch, and do its values exactly match the old constants?
4. Does "without a deploy" allow a restart, or is live reload required?

## Decision-maker summary

Do not merge. As written, any config mistake (missing file, wrong working directory, quoted or misspelled key, new plan) silently removes rate limiting from a shared production backend. Merging requires four things: fail-closed loading, real YAML parsing with validation, loader tests, and evidence that callers use the file with the correct values.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "ratelimit.py load_limits: except FileNotFoundError: pass; allowed: if limit is None: return True", "scenario": "Config file missing or not mounted -> empty limits -> every plan unlimited, shared backend unprotected, no error", "fix": "Fail closed: raise on missing/unreadable file at startup; deny or raise for unknown plans; test both"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "ratelimit.py allowed: limits.get(plan) -> True", "scenario": "Plan key mistyped or new plan added without config entry -> unlimited access (previously KeyError)", "fix": "Deny/raise for unknown plans; validate at load that all known plans have limits"},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "ratelimit.py LIMITS_PATH = \"config/limits.yaml\"", "scenario": "Process started with different CWD -> FileNotFoundError swallowed -> unlimited", "fix": "Resolve path via env var or absolute/module-relative path; fail if absent"},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "ratelimit.py parser: line.split(':', 1); int(n)", "scenario": "Valid YAML like inline comment or non-limit key raises uncaught ValueError; quoted key '\"free\": 100' stored with quotes -> lookup miss -> unlimited", "fix": "Use yaml.safe_load plus schema validation (known plan -> positive int), reject unknown/duplicate/invalid entries"},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "change.patch (no caller of load_limits; old hardcoded limits not removed)", "scenario": "Callers keep passing hardcoded dict; ops edits to YAML have no effect", "fix": "Include caller change, remove hardcoded limits, add integration test from file to allowed()"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "Requirement: change without a deploy", "scenario": "Limits loaded once at startup; ops edit has no effect until restart", "fix": "Clarify requirement; if needed add reload (SIGHUP/mtime) keeping last-good config on parse error"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "tests/test_ratelimit.py", "scenario": "No tests for load_limits, missing file, unknown plan, malformed lines; findings 1-4 ship with green tests", "fix": "Add loader and unknown-plan tests"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "PR.md: file and values added in commit 91c4e7a", "scenario": "91c4e7a not an ancestor of e07b3d8 or values differ from old constants -> missing file (unlimited) or wrong limits", "fix": "git merge-base --is-ancestor 91c4e7a e07b3d8; diff YAML values against removed constants"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "ratelimit.py parser", "scenario": "Duplicate keys last-wins silently; zero/negative limits accepted; locale-dependent encoding", "fix": "Validate on load; open with encoding='utf-8'"}
  ]
}
```