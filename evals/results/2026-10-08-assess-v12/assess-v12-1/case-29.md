VERDICT: try. ci-select is MIT, free and needs no account, and it plugs into the pytest + GitHub Actions setup we already have, so it plausibly serves goal 2 (cut CI minutes by a third). But the snapshot shows no evidence that its selection is correct or that it saves meaningful time, so it needs a bounded trial before we rely on it.

WHAT IT IS: example-org/ci-select on default branch `main` (no commit sha in the snapshot). License MIT. 2,100 stars, last push 2026-10-01, not archived. The README names release 2.1.0, dated 2026-10-01. Read from the saved snapshot and meta.json captured 2026-10-08, not live.

CLAIMS CHECKED:
- **"Picks only the tests a diff affects"** (the sender's words and the README's). Load-bearing.
  - Evidence: the README states it and shows usage (`pytest $(ci-select --diff origin/main)`).
  - It gives no method: nothing on how it maps changes to tests (imports, coverage, conftest/fixtures, data files).
  - Status: **UNVERIFIED**. The risk is that it silently skips tests that should run.
- **It serves goal 2** (the sender's question). Load-bearing.
  - Evidence: none. The item gives no figures on how many tests it skips or how many CI minutes it saves.
  - Status: **UNVERIFIED**. Whether it gets us a third off depends on our diff patterns and test layout.
- **Works with pytest.**
  - Evidence: the README states it, and the usage example is pytest.
  - Status: **PROBABLE**.
- **No network access, no telemetry.** Load-bearing for the data constraint.
  - Evidence: README statement only. No source was read.
  - Status: **PROBABLE**.
- **"One dependency (the standard library only)."** Not load-bearing.
  - Evidence: the README. The wording contradicts itself, since the standard library is not a dependency. The likely meaning is no third-party dependencies.
  - Status: **PROBABLE**.
- **MIT license.**
  - Evidence: the README and meta.json agree.
  - Status: **CONFIRMED**.
- **Actively maintained.**
  - Last release and last push are both 2026-10-01, and the repo is not archived: **CONFIRMED**.
  - "Issues answered within days" is the README's own claim: **UNVERIFIED**, not load-bearing.
- **2,100 stars.** Confirmed in meta.json, but popularity is not evidence that it works.

FIT:
- **Goal:** goal 2, cutting CI minutes by a third. It does not serve goals 1, 3 or 4.
- **Overlap:** none found. We use pytest and GitHub Actions, and no test-selection tool is in use.
- **Burden:**
  - One pinned pip dependency and a change to the CI test step.
  - In practice we would also want a scheduled full-suite run as a safety net, which gives back some of the savings.
- **Cost:** free, open source, MIT, no tier limits (read from the snapshot dated 2026-10-08). No account is needed. It fits the $0 budget.
- **Risks:**
  - The main risk is missed tests. The selection method is undocumented, so a change to conftest.py, fixtures or data files might not trigger the tests that depend on it.
  - The license is fine: MIT is allowed even if we vendor it in.
  - The install is a pinned PyPI version, not `curl | bash`.
  - No telemetry is claimed, but this is not verified in the source.
  - Lock-in is low: we can remove it by reverting one CI line.

NEXT ACTION:
- **Action:** on a branch, run ci-select alongside the full suite for two weeks of real PRs. For each PR, log:
  - the tests ci-select selected,
  - any failures in the full run that the selected set missed,
  - the CI minutes of each run.
- **Owner:** operator, or whoever owns the CI config.
- **Done when:** the two-week log shows the minutes saved per PR and the number of missed failures.
- **Stop condition:** stop and skip it if it misses any failing test that the full suite catches, or if the projected saving is well under a third of CI minutes.
- **Hand-off:** none. This is using a tool, not borrowing ideas from it.

CONFIDENCE: medium.
- What raises it: the item is resolved from the snapshot, the context file is present, and license, health and cost are confirmed.
- What limits it: the two claims the verdict rests on (correct selection and meaningful savings) are UNVERIFIED, and I worked from a saved snapshot, not the live repo or its source.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo", "identity": "example-org/ci-select@main (MIT, release 2.1.0, last push 2026-10-01, not archived, 2,100 stars; snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "picks only the tests a diff affects", "evidence": "README statement and usage example; no selection method described", "status": "UNVERIFIED"},
    {"claim": "using it serves goal 2 (cut CI minutes by a third)", "evidence": "none in the item; no benchmark or savings figures", "status": "UNVERIFIED"},
    {"claim": "works with pytest", "evidence": "README statement and pytest usage example", "status": "PROBABLE", "load_bearing": false},
    {"claim": "no network access and no telemetry", "evidence": "README statement only; source not read", "status": "PROBABLE"},
    {"claim": "one dependency (the standard library only)", "evidence": "README; wording self-contradictory, likely means no third-party deps", "status": "PROBABLE", "load_bearing": false},
    {"claim": "MIT license", "evidence": "README and meta.json agree", "status": "CONFIRMED"},
    {"claim": "actively maintained (last release 2026-10-01)", "evidence": "meta.json last_push 2026-10-01, not archived; README release date matches", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "issues answered within days", "evidence": "README self-report only", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "cut CI minutes by a third this quarter (goal 2)", "overlap": "none found; pytest and GitHub Actions in use, no test-selection tool",
          "burden": "one pinned pip dependency and a changed CI test step; a periodic full-suite run is advisable as a safety net",
          "risks": ["undocumented selection method may skip affected tests (conftest, fixtures, data files)", "MIT, allowed even if vendored", "no telemetry claimed but not verified in source", "low lock-in: one CI line to revert"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "On a branch, run ci-select alongside the full suite for two weeks of PRs, logging selected tests, failures it missed, and CI minutes per run",
                  "owner": "operator", "done_when": "two-week log shows minutes saved per PR and the count of missed failures",
                  "stop_condition": "stop if it misses any failure the full suite catches, or projected saving is well under a third of CI minutes", "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```