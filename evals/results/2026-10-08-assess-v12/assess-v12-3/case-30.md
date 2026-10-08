VERDICT: try. The method directly targets goal 2 (cut CI minutes by a third), and the reported median saving of 38% clears that bar, but it comes from a preprint read only as a short snapshot, so trial it on our own pytest suite before we rely on it.

WHAT IT IS: Paper 2609.02210, "Selecting tests by change impact: a 40-project study". It is a preprint posted 2026-09-14 and has not been peer reviewed. I read it from the saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live. The snapshot holds only abstract-level text: no methods section, no per-project data. The paper's data and scripts repository is linked but was not resolved.

CLAIMS CHECKED:
- **Change-impact selection cut CI time by a median 38% (IQR 29–47%) on 40 open-source projects.** The evidence is an observational study across 40 projects, with the measurement stated as CI time. The snapshot does not say whether the cost of the nightly full run is counted in that figure. **PROBABLE**, load-bearing.
- **It missed 1.4% of the failures a full run found, and a nightly full run recovered all of them.** The evidence is the same study. **PROBABLE**, load-bearing. This sets the safety pattern we would need to copy: selective runs on PRs plus a nightly full run.
- **It applies to Python projects; projects with heavy integration tests benefited less.** This is the paper's own stated limitation. **CONFIRMED** as what the paper says. It fits our Python 3.12 / pytest stack.
- **Data and scripts are MIT-licensed.** This is stated in the snapshot, but I did not read the repository or its license. **UNVERIFIED**, not load-bearing.
- **Inference (not stated by the paper): applying this would cut our CI minutes by a third.** Our own suite's mix of integration tests is unknown. The lower quartile (29%) falls below a third, and the extra nightly full run eats into the savings. **UNVERIFIED**, not load-bearing. Settling this is the point of the trial.

What would change the conclusion:
- The 38% excludes the nightly run's minutes.
- Our suite is dominated by integration tests.
- The full paper's methods show the selection was tuned per project.

FIT:
- **Goal:** goal 2, cutting CI minutes by a third this quarter.
- **Overlap:** none found. We run pytest on GitHub Actions with no test selection listed.
- **Burden:**
  - build or borrow dependency mapping between code and tests;
  - split CI into a selective PR job plus a nightly full-run job;
  - maintain the mapping as the code changes.
- **Cost:** reading a paper costs nothing. Any tool we would adopt from its repo is unread, so the budget impact is unknown; the expectation is $0.
- **Risks:**
  - about 1.4% of failures slip past PR checks until the nightly run;
  - savings shrink with integration-heavy suites;
  - the result is a preprint and not peer reviewed;
  - the repo's license is unread. It must be MIT, Apache-2.0 or BSD if we vendor anything from it.

NEXT ACTION:
- **Action:** hand the paper and its linked repository to `glean`. Extract the selection method and the nightly-recovery setup, then trial it for two weeks on our main repository's pytest job, measuring CI minutes against the previous two weeks. Count the nightly full run's minutes in the total.
- **Owner:** operator, or whoever maintains the CI.
- **Done when:** two weeks of CI minutes are compared, including the nightly run.
- **Stop condition:** stop if the net saving is under 20%, or if any failure reaches main that the nightly run did not catch before release.
- **Hand-off:** `glean`.

CONFIDENCE: medium.
- The item resolved, but only from a short saved snapshot without methods or data.
- The load-bearing claims are PROBABLE, from a non-peer-reviewed preprint.
- How well it transfers to our suite is unknown.
- The context file is present.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "paper", "identity": "2609.02210, 'Selecting tests by change impact: a 40-project study', preprint posted 2026-09-14, read from snapshot captured 2026-10-08", "resolved": true},
  "claims": [
    {"claim": "running only tests whose dependencies intersect a change cut CI time by a median 38% (IQR 29-47%) on 40 open-source projects", "evidence": "observational study of 40 projects as summarized in the snapshot; unclear whether nightly full-run minutes are counted", "status": "PROBABLE"},
    {"claim": "selection missed 1.4% of failures a full run found, and a nightly full run recovered all of them", "evidence": "same 40-project study, snapshot text only", "status": "PROBABLE"},
    {"claim": "covers Python and Java projects; integration-heavy projects benefited less", "evidence": "paper's stated limitations", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "data and scripts are in a linked MIT-licensed repository", "evidence": "stated in snapshot; repository and its license not read", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "applying it would cut our CI minutes by a third", "evidence": "inference from the median; our integration-test mix unknown, lower quartile 29%, nightly run adds minutes", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "cut CI minutes by a third this quarter (goal 2)", "overlap": "none found; pytest on GitHub Actions runs with no test selection",
          "burden": "dependency mapping from code to tests, a selective PR job plus a nightly full-run job, ongoing mapping upkeep",
          "risks": ["about 1.4% of failures reach main until the nightly run", "smaller savings if our suite is integration-heavy", "preprint, not peer reviewed", "repository license unread; must be MIT, Apache-2.0 or BSD if vendored"],
          "cost": {"price": "free", "tier": "paper", "limits": "none for the paper; any tooling from its repo unread", "terms": "repository stated MIT, not verified", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Hand the paper and its repository to glean for the selection method and the nightly-recovery setup, then trial it for two weeks on the main repo's pytest job, comparing CI minutes (nightly run included) with the prior two weeks",
                  "owner": "operator", "done_when": "two weeks of CI minutes, nightly run included, are compared with the prior two weeks",
                  "stop_condition": "stop if net saving is under 20% or any failure reaches main that the nightly run did not catch before release", "handoff": "glean"},
  "confidence": "medium",
  "context_file": "present"
}
```