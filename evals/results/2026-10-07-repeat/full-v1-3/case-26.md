**Review mode:** This is a single-context review without tools. I could not run the code or tests, open `config/limits.yaml`, or inspect commit 91c4e7a, so every finding below comes from reading the patch. The work was not written in this conversation, so I am not anchored on the author's reasoning. For a production rate-limit change, a second reviewer should still run the tests (below) before merge.

---

**VERDICT: REWORK.** The patch turns every configuration fault (missing file, wrong working directory, plan name typo, unmerged config commit) into unlimited access to the shared backend, and nothing tests or reports this.

**CONFIDENCE IN VERDICT: High.** The fail-open behavior is visible directly in the diff. It is limited by three things I could not see: the callers of `load_limits`/`allowed`, `config/limits.yaml`, and commit 91c4e7a.

### Pass 1: Reconstruct

The PR adds `load_limits()`, which reads `plan: number` lines from `config/limits.yaml`. It changes `allowed()` so that a plan with no configured limit is always allowed. It claims the config file and its values arrive in commit 91c4e7a and that tests pass.

For this to be correct, all of the following must hold:
- The file is present and readable at a path relative to the process working directory in every environment.
- Ops only ever write flat `name: integer` lines, never real YAML.
- Callers actually call `load_limits` in a way that picks up edits without a deploy.
- The hardcoded values were really removed and moved into the file.
- Treating "no limit known" as "unlimited" is acceptable for a backend the limits exist to protect. This last one is unstated.

### FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `load_limits`: `except FileNotFoundError: pass`. `allowed`: `if limit is None: return True` | Fails open, silently. A missing file gives `{}`, and every plan then becomes unlimited. Nothing is logged or raised. | The file is absent from the deploy artifact or container image, or a typo is made in its path. Every customer gets unlimited requests and the shared backend is unprotected. No alert fires. | Raise on a missing file, or fall back to a known safe default and log loudly. Decide fail-closed vs. fail-open explicitly. Add a test for the missing-file case. |
| 2 | Critical | PROBABLE | `LIMITS_PATH = "config/limits.yaml"` | The path is relative, so it resolves against the process CWD, not the module or repo. | The service is started by systemd, gunicorn, or a container with a different workdir. That leads to `FileNotFoundError`, then #1, then no limits. | Resolve relative to `__file__` or take the path from an env var or setting. Assert at startup that the file loaded and is non-empty. |
| 3 | High | CONFIRMED | `allowed`: `limits.get(plan)` returning `None` gives `True` | Silent semantic change. Before, an unknown plan raised `KeyError` (fail closed). Now an unknown plan is unlimited. The PR does not mention this. | A new plan `"team"` ships before ops adds it to the YAML, or ops writes `Free:` instead of `free:`. That plan becomes unlimited. | Treat an unknown plan as deny, or apply an explicit `default` limit. Document the behavior and test it. |
| 4 | High | CONFIRMED | `load_limits`: `int(n)` | This is a hand-rolled parser, not YAML, despite the `.yaml` name. Normal YAML input crashes it or misreads it. | `free: 100  # daily` raises `ValueError`. A nested `plans:` header gives `int("\n")` and raises `ValueError`. `"free": 100` produces the key `'"free"'`, which never matches, so that plan is unlimited via #3. `1e3` raises `ValueError`. None of these are caught, so whether the failure is a crash or a fallback depends on the unseen caller. | Use `yaml.safe_load` and validate the schema (a mapping of str to non-negative int). Reject unknown shapes with a clear error. Alternatively, rename the file to `.txt` or `.conf` so ops do not assume YAML. |
| 5 | High | UNVERIFIED | Whole patch; no caller of `load_limits` shown | The requirement is "change without a deploy." Nothing in the patch calls `load_limits`, and there is no reload. If it is called once at import or startup, a change needs a restart. If it is not called at all, the limits never apply. | Ops edit the file. Nothing changes until restart, or ever. | Show the call site. Implement reload on mtime change, a TTL, or a signal, and document how ops apply a change. |
| 6 | High | UNVERIFIED | PR.md: "the file and its values are added in commit 91c4e7a" | The config file is not in this diff. The PR head is e07b3d8 and the merge base is 5a1c2f6. Whether 91c4e7a is between them, already on main, or elsewhere cannot be shown. | 91c4e7a is not on the merge path. The file is missing in prod, which triggers #1. | Confirm with `git merge-base --is-ancestor 91c4e7a e07b3d8`. Then review the file's values against the old hardcoded ones. |
| 7 | Medium | UNVERIFIED | base/ratelimit.py has no hardcoded limits | The "move out of code" claim cannot be checked. The old values are not in the diff, so either they live in an unchanged caller (still hardcoded) or they were deleted somewhere not shown. | Two sources of truth, or values changed during the move without notice. | Include the removal diff of the old constants. Have a test compare the shipped YAML values with the old ones. |
| 8 | Medium | CONFIRMED | `tests/test_ratelimit.py` | The test covers only the pre-existing path, a known plan with a dict. It covers none of the new code: `load_limits`, the missing file, an unknown plan, malformed lines. "Tests pass" is true but says nothing about the change. | Any of #1 to #4 regress unnoticed. | Add tests for: a file that parses; a missing file; an unknown plan; inline comments; quoted keys; non-int values; blank lines; duplicates. |
| 9 | Low | CONFIRMED | `load_limits` loop | Duplicate keys are silently last-wins. Negative values are accepted. `open()` has no `encoding`. | `free: 100` and later `free: 10000` from a bad merge means the higher value wins silently. | Reject duplicates and negatives. Pass `encoding="utf-8"`. |

### WHAT HOLDS UP
- The core comparison `used_today < limit` is unchanged and correct for known plans.
- Comment lines (including indented ones) and lines with no colon are skipped correctly.
- `split(":", 1)` and `int()` tolerate surrounding whitespace and a trailing newline.

### UNVERIFIED CLAIMS
- **"Tests pass."** Run `python -m unittest discover -s tests` from the repo root. Note that `import ratelimit` from `tests/` depends on `sys.path`.
- **"The file and its values are added in commit 91c4e7a."** Check ancestry with `git merge-base --is-ancestor 91c4e7a e07b3d8`, then inspect `git show 91c4e7a:config/limits.yaml`.
- **"Operations can change limits without a deploy"** (implied by the PR's purpose). Show the call site and the reload mechanism.

### QUESTIONS FOR THE AUTHOR
1. Where is `load_limits` called, and how often? How does an edit take effect without a restart or deploy?
2. Is fail-open (unlimited) on a missing file or unknown plan intentional? Who signed off on that for a backend the limits are meant to protect?
3. Is 91c4e7a an ancestor of e07b3d8, and where did the old hardcoded values live?

### DECISION-MAKER SUMMARY
Do not merge. A missing config file, wrong working directory, or plan name typo removes all rate limiting with no error, and the tests do not cover any of the new code. Rework it to:
- fail closed or loudly,
- use a real YAML parser with validation,
- show the reload path and the provenance of the config file.

If merged as is, the risk is an unannounced, unlimited load on the shared production backend.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "ratelimit.py load_limits `except FileNotFoundError: pass` + allowed `if limit is None: return True`", "scenario": "Config file absent from deploy artifact or wrong path: limits == {}, every plan unlimited, no log or alert; shared backend unprotected.", "fix": "Raise or log loudly on missing file; choose explicit fail-closed/default behavior; add missing-file test."},
    {"severity": "Critical", "evidence_level": "PROBABLE", "location": "ratelimit.py LIMITS_PATH = \"config/limits.yaml\"", "scenario": "Service started with a different CWD (systemd, gunicorn, container workdir) -> FileNotFoundError -> silently unlimited.", "fix": "Resolve path relative to __file__ or from env/settings; assert non-empty limits at startup."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "ratelimit.py allowed: limits.get(plan) is None -> True", "scenario": "Unknown or misspelled plan (new plan not yet in YAML, 'Free' vs 'free') gets unlimited access; previously raised KeyError. Change not disclosed in PR.", "fix": "Deny or apply explicit default limit for unknown plans; document and test."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "ratelimit.py load_limits `int(n)` hand-rolled parser", "scenario": "Valid YAML such as inline comments ('free: 100  # daily'), nested mapping ('plans:'), quoted keys, or '1e3' raises uncaught ValueError or produces non-matching keys, leading to a crash or unlimited plan.", "fix": "Use yaml.safe_load with schema validation (str -> non-negative int), clear errors; or stop calling it YAML."},
    {"severity": "High", "evidence_level": "UNVERIFIED", "location": "Whole patch: no caller of load_limits, no reload mechanism", "scenario": "Ops edit config but change needs restart (or limits are never loaded), so the 'without a deploy' requirement is unmet.", "fix": "Show call site; implement mtime/TTL/signal reload; document the ops procedure."},
    {"severity": "High", "evidence_level": "UNVERIFIED", "location": "PR.md: 'the file and its values are added in commit 91c4e7a'", "scenario": "91c4e7a not in merge-base..head range, so config file missing in prod, causing fail-open everywhere.", "fix": "git merge-base --is-ancestor 91c4e7a e07b3d8; review file values against old hardcoded values."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "base/ratelimit.py contains no hardcoded limits; removal not in diff", "scenario": "Old constants remain in an unchanged caller (two sources of truth) or values changed during the move unnoticed.", "fix": "Include removal diff of old constants; add test comparing shipped config to previous values."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "tests/test_ratelimit.py", "scenario": "Only tests the known-plan dict path; load_limits, missing file, unknown plan, malformed lines are untested, so regressions in the new logic go unnoticed.", "fix": "Add tests for parse, missing file, unknown plan, inline comment, quoted key, non-int value, duplicates."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "ratelimit.py load_limits loop and open()", "scenario": "Duplicate keys silently last-wins; negative limits accepted; platform-dependent encoding.", "fix": "Reject duplicates and negatives; open with encoding='utf-8'."}
  ]
}
```