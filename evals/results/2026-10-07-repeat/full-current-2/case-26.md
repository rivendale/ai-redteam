**Review of PR #63: per-plan limits moved to a config file**

**VERDICT: REWORK.** If the config file is missing, unreadable, or found relative to the wrong working directory, every plan becomes unlimited, and nothing is logged. That removes the protection this shared backend depends on.

**CONFIDENCE: medium.** Limits:
- No tools, so nothing was run. "Tests pass" and all runtime behaviour are inferred from reading the code.
- `config/limits.yaml` and commit 91c4e7a were not supplied.
- No callers of `ratelimit` were shown.
- This was a single-reviewer pass with no fresh subagent. The reviewer did not write the work, but re-run the review with tools before merge.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, PR.md, base/README.md, base/ratelimit.py, change.patch.
- **Not seen: `config/limits.yaml`.** This matters. Its values, format and presence decide whether limits work at all. `change.patch` does not add it.
- **Not seen: commit 91c4e7a.** This matters. It is unknown whether this commit is between merge base 5a1c2f6 and head e07b3d8. If it is not, merging this PR ships no config file.
- **Not seen: callers of `allowed()` and `load_limits()`.** This matters. When and how often limits are loaded decides whether operations can change them without a deploy.
- **Not seen: the previous hardcoded limit values.** This matters. `base/ratelimit.py` already takes `limits` as a parameter, so the old values live somewhere not supplied. There is no way to check that the config values match them.
- **Not seen: CI or test output.** This matters a little. "Tests pass" is unverified, and the tests do not cover the change anyway (finding 4).

**SEATS AND GATE**
- **Gate:** passed. No personal data, credentials or confidential material.
- **Seats:** one local reviewer. No subagent or cross-vendor seats were available in this session.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED (code read) | B | change.patch `load_limits`: `except FileNotFoundError: pass`; `allowed`: `if limit is None: return True` | A missing config file returns `{}`, and an empty dict makes `allowed()` return True for every plan. Nothing is logged. | The file is not deployed, is renamed, or the process starts from another directory. Every customer gets unlimited requests and the shared backend has no protection. Nothing alerts anyone. | Fail closed: raise when the file is missing or empty, at startup and on reload. On reload, keep the last good limits. Log and alert on any load failure. Add a test that a missing file raises. | confirmed. The docstring says this is intentional ("no limits are configured"), but documenting fail-open does not make it safe for a control that protects a shared backend. |
| 2 | High | CONFIRMED (code read) | B | `LIMITS_PATH = "config/limits.yaml"` | The path is relative to the process working directory, not to the module or the deployment root. | In production, a service manager or container starts the process with a different working directory. `open` raises `FileNotFoundError`, which is swallowed, and finding 1 follows. This happens silently even when the file is correctly deployed. | Resolve the path from an environment variable or an absolute path, or relative to `__file__`. Fail if the path does not exist. | confirmed. Python resolves relative `open()` paths against the working directory. |
| 3 | High | CONFIRMED (code read) | B | `allowed`: `limits.get(plan)` then `return True` | Behaviour change: a plan missing from the config (a typo, or a new plan nobody added) used to raise `KeyError` and is now unlimited. | Operations add plan "team" in code but forget the config line, or type `Pro:` instead of `pro:`. That plan's traffic is unlimited and nothing signals it. | Treat an unknown plan as denied or as the most restrictive limit, and log it. Validate at load time that every known plan has a limit. Add a test for an unknown plan. | confirmed. Its strongest defence is "avoid 500s for unknown plans", but that argues for deny-with-log, not allow-unlimited. |
| 4 | Medium | CONFIRMED (code read) | B | tests/test_ratelimit.py | The only test exercises `allowed()` with a dict, which behaves the same on base and head. It never tests `load_limits`, a missing file, an unknown plan, or malformed input. It would pass against the pre-PR code, so it cannot catch a regression in this change. "Tests pass" says nothing about the new behaviour. | Findings 1 to 3 and 5 all ship with green CI. | Add tests: parse a sample file; missing file; unknown plan; malformed value; inline comment. Mutation check: make `load_limits` return `{}` and confirm a test goes red. | n/a (Medium) |
| 5 | Medium | CONFIRMED (code read) | B | `load_limits` parsing loop | The `.yaml` file is parsed by hand, line by line. Valid YAML that operations might write breaks it: `free: 100  # daily` and a nested `limits:` header both raise `ValueError` from `int()`. Quoted keys such as `"free": 100` are stored with their quotes. Duplicate keys silently override. Negative or zero values are accepted. | Operations add an inline comment during an incident. Loading raises, causing a crash at startup or failed requests at runtime, depending on the caller. Or a quoted key becomes an unknown plan and finding 3 follows. | Use a real YAML parser (`yaml.safe_load`) with schema validation: known plans, positive integers. Or rename the file and document the strict format. Validate in CI before the file reaches production. | n/a |
| 6 | Medium | UNVERIFIED | A/B | Callers not supplied; request says "without a deploy" | Nothing shows when `load_limits()` runs. If it runs once at import or startup, a change needs a restart and does not meet the request. If it runs per request, it re-reads the file on every request, which costs I/O and can read a half-written file mid-edit. | Operations edit the file during an incident and nothing changes until a restart. Or a partial write during the edit triggers finding 1 or 5. | Show the call site. Implement reload on a timer, a signal or file modification time, with atomic replacement of the file and last-good fallback. | n/a |
| 7 | Medium | UNVERIFIED | C | PR.md: "the file and its values are added in commit 91c4e7a" | The config file is not in the patch, and its values were not supplied. There is no evidence the values match the old hardcoded limits, or that 91c4e7a is in this PR's range. | Merging ships code without the config, which triggers finding 1. Or the values differ from the old limits, which silently loosens or tightens customers' quotas. | Include the file in the PR diff. Show the old values next to the new ones. Confirm 91c4e7a is an ancestor of e07b3d8 and a descendant of 5a1c2f6. | n/a |

**WHAT HOLDS UP**
- The core comparison `used_today < limit` is unchanged and correct for configured plans.
- Comment lines and blank lines are skipped correctly.
- `split(":", 1)` handles values that contain a colon.
- The change is small and keeps the `allowed()` signature, so callers do not need to change.

**UNVERIFIED CLAIMS**
- **"Tests pass":** run CI on e07b3d8 and look at the output. This is also weak evidence; see finding 4.
- **"The file and its values are added in commit 91c4e7a":** check with `git merge-base --is-ancestor`, and diff the values against the old hardcoded limits.
- **Operations can change limits without a deploy:** show the reload path.

**QUESTIONS FOR THE AUTHOR**
1. Is fail-open on a missing file or an unknown plan intentional? Who signed off on running the shared backend unprotected in that state?
2. Where is `load_limits()` called, and when do edits to the file take effect?
3. Is 91c4e7a in this PR? Where are the old hardcoded values, and do the new ones match?
4. What working directory does the production process run in?

**DECISION-MAKER SUMMARY**
Do not merge. Any config mistake (missing file, wrong working directory, unlisted plan) silently removes all rate limits from a shared production backend, and the tests cover none of the new code. Fail closed, use an absolute or configured path, parse real YAML with validation, and add tests for the failure cases before merging.

**OWNER SUMMARY**
This change moves the request limits into a settings file, but if that file is missing or can't be found, the system quietly lets every customer make unlimited requests. That could overload the shared backend without anyone noticing. It needs to refuse to run without valid limits, and it needs tests for that, before it goes live.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "config/limits.yaml", "status": "not_seen", "matters": true},
    {"item": "commit 91c4e7a", "status": "not_seen", "matters": true},
    {"item": "callers of allowed()/load_limits()", "status": "not_seen", "matters": true},
    {"item": "previous hardcoded limit values", "status": "not_seen", "matters": true},
    {"item": "CI/test output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "change.patch ratelimit.py load_limits (except FileNotFoundError: pass) + allowed (limit is None -> True)",
     "scenario": "Config file missing, renamed or not deployed: load_limits returns {} and allowed() returns True for every plan, silently; the shared backend is unprotected.",
     "fix": "Fail closed on a missing or empty file; keep the last good limits on reload; log and alert on load failure; add a missing-file test.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "change.patch ratelimit.py LIMITS_PATH = \"config/limits.yaml\"",
     "scenario": "Path resolves against the working directory; a production process started from another directory gets FileNotFoundError, which is swallowed, leading to unlimited requests.",
     "fix": "Resolve from an environment variable, an absolute path or __file__; fail if absent.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "change.patch ratelimit.py allowed(): limits.get(plan) / return True",
     "scenario": "A plan missing from the config (typo, new plan) was a KeyError and is now unlimited, silently.",
     "fix": "Deny or apply the most restrictive limit for unknown plans and log it; validate at load that every known plan has a limit; add a test.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "tests/test_ratelimit.py",
     "scenario": "The only test passes on pre-PR code and never calls load_limits; fail-open, unknown-plan and parse-error paths ship with green CI.",
     "fix": "Add tests for parsing, a missing file, an unknown plan, a malformed value and an inline comment; mutate load_limits to return {} and confirm a test goes red.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "change.patch ratelimit.py load_limits parsing loop",
     "scenario": "Valid YAML such as 'free: 100 # note' or a nested 'limits:' header raises ValueError; quoted keys keep their quotes and become unknown plans; negative values and duplicate keys are accepted silently.",
     "fix": "Use yaml.safe_load with schema validation (known plans, positive ints), validated in CI.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "A", "location": "callers of load_limits() (not supplied); request 'without a deploy'",
     "scenario": "If limits load once at startup, operations changes need a restart; if per request, there is file I/O on every request and a risk of reading a half-written file.",
     "fix": "Show the call site; add timed, signal or mtime reload with atomic file replacement and last-good fallback.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "C", "location": "PR.md: 'the file and its values are added in commit 91c4e7a'",
     "scenario": "The config file is not in the patch; if 91c4e7a is outside the PR range, the merge ships without config (finding 1); the values may differ from the old hardcoded limits.",
     "fix": "Include the file in the PR diff; confirm the ancestry of 91c4e7a; diff the values against the previous limits.", "status": "n/a"}
  ]
}
```