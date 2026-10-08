VERDICT: try. The paper reports a median 38% cut in CI time on Python and Java projects, which is above goal 2's one-third target, but whether it reaches a third on our own pytest suite is untested. A bounded measurement on our repo will settle it.

WHAT IT IS: Paper 2609.02210, "Selecting tests by change impact: a 40-project study". It is a preprint posted 2026-09-14. I read it from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live. The snapshot does not give the authors or a venue, and it holds only abstract-level text. The paper links a data and scripts repository it calls MIT; I have not read that repository.

CLAIMS CHECKED:
- **"Running only tests whose dependencies intersect a change cut CI time by a median 38% (IQR 29–47%)."**
  - Evidence: an observational study of 40 open-source projects, measuring CI time. The full method is not in the snapshot.
  - Status: PROBABLE. It is the paper's own reported data in a preprint, not peer-reviewed, and the method is unread.
  - Load-bearing.
- **"It missed 1.4% of the failures a full run found, and a nightly full run recovered all of them."**
  - Evidence: the same study.
  - Status: PROBABLE.
  - Load-bearing: this is what makes the approach safe enough to try.
- **"It applies to Python projects."**
  - Evidence: the paper's own limitations section names Python and Java only.
  - Status: CONFIRMED. That covers our Python 3.12 / pytest stack.
  - Load-bearing.
- **"Projects with heavy integration tests benefited less."**
  - Evidence: the paper's limitations section.
  - Status: CONFIRMED as stated.
  - Not load-bearing, but it bounds the expected gain.
- **Sender's implied claim: "it would cut our CI minutes by a third (goal 2)."** I split this into two parts:
  - *Fact:* the median of 38% is above 33%. CONFIRMED arithmetic.
  - *Inference:* we would get at least 33%. UNVERIFIED. The lower quartile (29%) is below a third. The paper measures time per run, not total minutes, and the nightly full run it relies on adds minutes back. Our share of integration tests is unknown.
  - Not load-bearing, because the trial exists to test it.
- **"Data and scripts are in an MIT repository."**
  - Evidence: the paper says so.
  - Status: UNVERIFIED. I have not read the repository or its license file.
  - Not load-bearing.

FIT:
- **Goal:** Goal 2, cut CI minutes by a third this quarter.
- **Overlap:** None found. Nothing in use does test selection; pytest and GitHub Actions run the full suite.
- **Burden:**
  - A change-to-test dependency mapping step in CI.
  - A new nightly full-run workflow.
  - Ongoing upkeep of the dependency map.
- **Cost:** Free. It is a paper, and its scripts are said to be MIT, which fits our license rules if we vendor them (to verify). Checked 2026-10-08 from the snapshot.
- **Risks:**
  - It is a preprint, not peer-reviewed.
  - About 1.4% of failures can reach main until the nightly run catches them.
  - The gain may be under a third if our suite is integration-heavy.
  - The nightly full run offsets part of the saving.

NEXT ACTION: The operator hands the paper to `glean` to extract the selection method. Then, on a branch, they replay the last 4 weeks of commits through the selection rule and compare it with the full pytest runs.
- **Done when:** we have total CI minutes (selected runs plus a nightly full run) set against the current minutes, and a count of the failures that were missed.
- **Stop if:** the projected saving is under 25%, or any missed failure would not be caught by the nightly run.
- **Hand-off:** `glean`.

CONFIDENCE: Medium.
- The paper is resolved, a context file is present, and the load-bearing claims are PROBABLE or CONFIRMED.
- Confidence is limited because I read only an abstract-level snapshot, not the full method, and the repository and its license are unread.
- Whether the gain reaches a third on our suite is unknown until the trial.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "paper",
           "identity": "2609.02210, 'Selecting tests by change impact: a 40-project study', preprint posted 2026-09-14 (read from snapshot captured 2026-10-08; authors not in snapshot)",
           "resolved": true},
  "claims": [
    {"claim": "running only tests whose dependencies intersect a change cut CI time by a median 38% (IQR 29-47%)",
     "evidence": "the paper's 40-project observational study; preprint, method not in snapshot", "status": "PROBABLE"},
    {"claim": "missed 1.4% of failures a full run found; a nightly full run recovered all of them",
     "evidence": "same study, as reported in the snapshot", "status": "PROBABLE"},
    {"claim": "applies to Python projects",
     "evidence": "paper's limitations: Python and Java projects only", "status": "CONFIRMED"},
    {"claim": "projects with heavy integration tests benefited less",
     "evidence": "paper's limitations section", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "the median saving (38%) exceeds goal 2's one-third target",
     "evidence": "arithmetic on the reported median", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "it would cut our CI minutes by a third (sender's implied claim)",
     "evidence": "nothing settles it: lower quartile is 29%, paper measures time per run not total minutes, nightly run adds minutes back, our integration-test share unknown",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "data and scripts are in an MIT-licensed repository",
     "evidence": "stated in the paper; repository not read", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "cut CI minutes by a third this quarter (goal 2)",
          "overlap": "none found; pytest and GitHub Actions run the full suite, no test selection in use",
          "burden": "dependency-mapping step in CI, a nightly full-run workflow, upkeep of the map",
          "risks": ["preprint, not peer-reviewed",
                    "about 1.4% of failures reach main until the nightly run",
                    "gain may fall below a third if our suite is integration-heavy",
                    "nightly full run offsets part of the saving",
                    "repository license stated as MIT but not read"],
          "cost": {"price": "free", "tier": "paper; scripts said to be open source",
                   "limits": "none", "terms": "MIT as stated by the paper, not verified",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "glean the paper's selection method, then replay the last 4 weeks of commits through it on a branch and compare against full pytest runs",
                  "owner": "operator",
                  "done_when": "projected total CI minutes (selected runs plus a nightly full run) set against current minutes, and missed failures counted",
                  "stop_condition": "stop if projected saving is under 25% or any missed failure would not be caught by the nightly run",
                  "handoff": "glean"},
  "confidence": "medium",
  "context_file": "present"
}
```