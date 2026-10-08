VERDICT: try. A bounded CI trial of change-impact test selection serves goal 2 directly: the reported median saving (38%) is above our one-third target, we run Python and pytest, which the study covered, and the trial costs no money and adds no account.

WHAT IT IS: Paper 2609.02210, "Selecting tests by change impact: a 40-project study", posted 2026-09-14 as a preprint (not peer-reviewed). Read from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json). The snapshot holds only the abstract-level summary, not the methods section or the linked repository.

CLAIMS CHECKED:
- **Median CI time cut of 38% (IQR 29–47%).** The evidence is a 40-project open-source study, measuring CI time when only tests whose dependencies intersect a change are run. PROBABLE. The design is reasonable and the data is said to be public, but it is the authors' own preprint result and I could not read the method. The verdict rests on this claim.
- **Selection missed 1.4% of the failures a full run found.** Same study, compared against full runs. PROBABLE. The verdict rests on this claim.
- **A nightly full run recovered every missed failure.** Same study. PROBABLE. The verdict rests on this claim, because it is the safety net that makes the misses acceptable.
- **Applies to Python projects.** The paper's own limitations say the sample was Python and Java only. CONFIRMED, as far as the scope of the study goes. The verdict rests on this claim.
- **Data and scripts are public under MIT.** The snapshot says so, but I did not read the repository. UNVERIFIED. The verdict does not rest on this.
- **Projects with heavy integration tests benefited less.** This is the paper's own limitation. CONFIRMED as stated. The verdict does not rest on this, but it is a risk for us.
- **What would change the conclusion:** our suite turning out to be integration-heavy, or the nightly full run eating most of the per-PR savings.

FIT:
- **Goal served:** goal 2, "Cut CI minutes by a third this quarter".
- **Overlap:** none found. Nothing in our stack selects tests. Today pytest runs the full suite in GitHub Actions.
- **Burden:** dependency-mapping or selection logic in CI, plus a new nightly full-suite job and its upkeep.
- **Cost:** free. It is a paper, and its scripts are said to be under MIT. Checked 2026-10-08.
- **Risks:**
  - The 38% is gross. The nightly full run adds minutes back, so the net saving may land below a third.
  - Our suite's mix of integration tests is unknown.
  - It is a preprint, read from a summary only.
  - A 1.4% miss rate means some failures reach main for up to a day.
  - The MIT license is unverified. It must be MIT, Apache-2.0 or BSD before we vendor any of the scripts.

NEXT ACTION: The operator (or whoever owns CI) gleans the selection method from the paper and its repository. They then run it in shadow mode on PR CI for 2 weeks: the full suite still runs and gates as usual, and the selected subset is recorded alongside it.
- **Done when:** two weeks of PRs show the minutes the selected subset would have used and the failures it would have missed, compared with the full runs. The net saving includes the cost of the nightly full run.
- **Stop condition:** stop if the projected net saving, after the nightly run, is under 20%, or if the projected miss rate is over 3%.
- **Hand-off:** `glean`.

CONFIDENCE: medium. I read only an abstract-level snapshot of a preprint, and the core numbers are PROBABLE, not independently checked. We also do not know how integration-heavy our own test suite is.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "paper", "identity": "2609.02210, 'Selecting tests by change impact: a 40-project study', preprint posted 2026-09-14 (saved snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "selecting tests by change impact cut CI time by a median 38% (IQR 29-47%)", "evidence": "the authors' own 40-project open-source study; preprint, method not in snapshot", "status": "PROBABLE"},
    {"claim": "selection missed 1.4% of failures a full run found", "evidence": "same study, compared against full runs", "status": "PROBABLE"},
    {"claim": "a nightly full run recovered all missed failures", "evidence": "same study", "status": "PROBABLE"},
    {"claim": "the result applies to Python projects", "evidence": "paper's limitations: sample was Python and Java only", "status": "CONFIRMED"},
    {"claim": "data and scripts are public under MIT", "evidence": "snapshot says so; repository not read", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "projects with heavy integration tests benefited less", "evidence": "paper's own stated limitation", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "Cut CI minutes by a third this quarter (goal 2)",
          "overlap": "none found; pytest in GitHub Actions currently runs the full suite with no test selection",
          "burden": "selection logic in CI plus a new nightly full-suite job to maintain",
          "risks": ["nightly full run offsets part of the gross 38% saving; net may fall short of a third",
                    "benefit drops for integration-heavy suites; our mix is unknown",
                    "preprint, read from an abstract-level snapshot only",
                    "1.4% of failures could reach main until the nightly run",
                    "script license unverified; must be MIT/Apache-2.0/BSD to vendor"],
          "cost": {"price": "free", "tier": "paper; scripts said to be open source", "limits": "none",
                   "terms": "scripts said to be MIT (unverified)", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Glean the selection method from the paper and its repository, then run it in shadow mode on PR CI for two weeks alongside the full suite",
                  "owner": "operator",
                  "done_when": "two weeks of PRs compared: minutes the selected subset would use and failures it would miss vs. full runs, with net saving including the nightly full run",
                  "stop_condition": "stop if projected net saving after the nightly run is under 20% or the projected miss rate exceeds 3%",
                  "handoff": "glean"},
  "confidence": "medium",
  "context_file": "present"
}
```