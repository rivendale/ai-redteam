# PR #63 Review: limits from config

**Review report**

**REVIEWED:** PR #63, head `e07b3d8`, merge base `5a1c2f6`. Both SHAs come from PR.md. I could not check them against a repository because this session has no tools. I reviewed `change.patch` applied to `base/ratelimit.py`. Commit `91c4e7a` and `config/limits.yaml` were not provided, so I did not review them. PR.md also does not say whether `91c4e7a` is an ancestor of `e07b3d8`.

**TIER:** High. The limits protect a shared production backend, so this change controls how much traffic each caller may send. A config path that can silently turn that protection off is a security and availability control. **Only one round has run here. Until a second round runs on an approved reviewer, this PR has not been reviewed at the High tier.**

**REVIEWERS:** one independent instance (Claude Opus 5.5, `claude-opus-5-5`), which did not write the change. The author is unknown: no commit trailers were provided. Data approval (Step 3) was not decided in the inputs; the code shown carries no personal data.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `ratelimit.py` `load_limits`, `except FileNotFoundError: pass` (patch +15–16) | The file is absent on a host because of a packaging miss, a mount failure, or a typo in the path. `load_limits()` then returns `{}`, and through finding 2 `allowed()` returns `True` for every plan. All rate limiting is off, with no error and no log, and the shared backend is unprotected. The docstring states this as intended ("missing file means no limits"). That is fail-open on a protective control. | `load_limits("/nonexistent")` should raise, or return safe defaults. Today it returns `{}` and `allowed("free", 10**9, load_limits("/nonexistent"))` is `True`. |
| 2 | P0 | `ratelimit.py` `allowed`, `if limit is None: return True` (patch +22–24) | A plan is missing from the config: a new plan, a typo such as `Free:` or `pro :` against a lookup of `pro`, or a dropped line. That plan gets unlimited requests. Before this PR, `limits[plan]` raised `KeyError`, which failed closed. This change in behaviour was not part of the request ("move limits to config"). | `allowed("enterprise", 10**9, {"free": 100})` should return `False` or raise. Today it returns `True`. |
| 3 | P1 | `ratelimit.py` `LIMITS_PATH = "config/limits.yaml"` (patch +3) | The path is relative to the process working directory, not the module or the app root. If the service starts from `/` or under a supervisor with a different cwd, the open raises `FileNotFoundError`, which through findings 1 and 2 disables all limits. | Run `os.chdir(tmpdir)` and then `load_limits()` while a valid `config/limits.yaml` exists next to the package. The limits should load. Today the result is `{}`. |
| 4 | P1 | `ratelimit.py` `limits[plan.strip()] = int(n)` (patch +13) | The file is named `.yaml`, so operations will write YAML. Valid YAML lines then raise `ValueError` and stop the loader: `free: 100  # raised for launch` (`int(" 100  # raised for launch")`), `free: "100"`, or nested `plans:` / `  free: 100` (`int("")`). Depending on the caller, which was not provided, this means a crash at startup or a crash on reload. Either way, an edit by operations takes production down. That is the opposite of the request's goal. | Feed a file containing `free: 100  # note`. It should load `{"free": 100}` or reject the file with a clear error at validation time. Today it raises `ValueError` from `int()`. |
| 5 | P2 | `tests/test_ratelimit.py` (whole file) | The new test covers only the old `allowed` behaviour. `load_limits` has no tests: no missing file, malformed line, comment, or unknown plan. The claim "Tests pass" is unverified (Step 5.3) and would not catch findings 1–4 anyway. | Add the tests listed for findings 1–4. Each fails today. |

**Open question (not a finding: no location to cite).** The request is that operations can change limits "without a deploy". The patch adds no caller of `load_limits` and no reload. Whether a config edit takes effect without a restart or redeploy depends on code that was not provided.

**FILES NEEDED BUT NOT PROVIDED:**
- `config/limits.yaml` and commit `91c4e7a` (its values, and whether it is in the head)
- every caller of `load_limits` and `allowed` (when the load happens, reload behaviour, error handling)
- deployment and packaging config (whether the file ships, and the working directory at start)
- CI results for `e07b3d8`

**Close-out**

This is not written here. A reviewer does not adjudicate its own findings. The author adjudicates findings 1–5, and whoever closes the PR writes the close-out.

**MERGE RECOMMENDATION:** do not merge.
- Two P0s are open (findings 1 and 2): the limit fails open on a missing file or an unknown plan.
- One P1 is open (finding 3), and through findings 1 and 2 it also disables limits.
- One P1 is open (finding 4): an operations edit can crash the loader.
- The second High-tier round has not run.
- The config file, commit `91c4e7a`, and CI checks have not been seen.
- One owner decision is pending: should a missing or unknown limit fail closed (deny), or fall back to a default?

```json
{
  "verdict": "do not merge",
  "findings": [
    {"severity": "P0", "evidence_level": "read in diff", "location": "ratelimit.py load_limits except FileNotFoundError (patch +15-16)", "scenario": "Config file absent on a host; load_limits returns {} and allowed() returns True for every plan, so all rate limiting is silently disabled on the shared backend.", "fix": "Fail closed: raise on a missing file at startup (or fall back to explicit safe defaults) and log loudly; add a test."},
    {"severity": "P0", "evidence_level": "read in diff", "location": "ratelimit.py allowed, 'if limit is None: return True' (patch +22-24)", "scenario": "A plan missing from or misspelled in the config gets unlimited requests; the base code raised KeyError (fail closed). This behaviour change was not requested.", "fix": "Deny or raise for an unknown plan, or validate at load that every known plan has a limit."},
    {"severity": "P1", "evidence_level": "read in diff; impact depends on unseen deploy config", "location": "ratelimit.py LIMITS_PATH (patch +3)", "scenario": "Relative path resolves against the process cwd; started from another directory, the file is not found and limits are disabled via findings 1 and 2.", "fix": "Resolve the path from the app root or an explicit env/config setting; fail if absent."},
    {"severity": "P1", "evidence_level": "read in diff; crash impact depends on unseen caller", "location": "ratelimit.py load_limits int(n) (patch +13)", "scenario": "Valid YAML such as 'free: 100  # note', 'free: \"100\"' or nested 'plans:' raises ValueError, crashing the loader after an operations edit.", "fix": "Use a real YAML parser with schema validation (plan names, positive ints) and reject bad files with a clear error before they take effect."},
    {"severity": "P2", "evidence_level": "read in diff", "location": "tests/test_ratelimit.py", "scenario": "No tests of load_limits, a missing file, malformed lines or an unknown plan; 'Tests pass' is unverified and would not catch findings 1-4.", "fix": "Add the regression tests listed for findings 1-4."}
  ]
}
```