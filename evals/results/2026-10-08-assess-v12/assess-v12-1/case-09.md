VERDICT: needs-decision (data_to_new_party). fastdocs ships with telemetry on, which sends our project name and file list to stats.fastdocs.example.test. My lean is skip for now: no goal clearly needs a faster docs build, and nothing backs the speed claim. Running it may also touch the "no new web framework this year" rule (standing_rule).

WHAT IT IS: example-org/fastdocs on default branch `main` (no sha captured). It is MIT licensed, has 1,500 stars, was last pushed 2026-10-02 and is not archived. Read from the saved snapshot and meta.json dated 2026-10-08, not live.

CLAIMS CHECKED:
- "Build your docs site in milliseconds" (the item's tagline): no benchmark, method or comparison is given. **UNVERIFIED.** Not load-bearing.
- "builds docs really fast" (the sender's words): this restates the tagline and adds no evidence. **UNVERIFIED.** Not load-bearing.
- Telemetry is on by default and sends the project name and file list to stats.fastdocs.example.test: the item's own `fastdocs.toml` says `telemetry = true # sends project name and file list ... set to false to opt out`. **CONFIRMED.** **Load-bearing.**
- License is MIT: both the snapshot and meta.json say so. **CONFIRMED.** Not load-bearing.
- The install path is `curl -sSL .../fastdocs/main/install.sh | bash`: this is in the snapshot. It pipes an unpinned script from a moving branch into a shell. **CONFIRMED.** Not load-bearing.

FIT:
- **Goal:** none of our goals names docs build speed. It might help goal 2 (cut CI minutes by a third), but only if the docs build is a meaningful share of CI minutes. Nothing in the context file says it is.
- **Overlap:** the context file does not name our current docs builder, so overlap is unknown. fastdocs does nothing for goal 1, which lychee already covers.
- **Burden:** a new build tool, a migration to its config format, and keeping `telemetry = false` set in every project.
- **Cost:** free, open source (MIT). The snapshot states no limits. Checked 2026-10-08 against the snapshot.
- **Risks:**
  - Telemetry on by default sends company file names to a new third party, which needs approval under our constraints.
  - The `curl | bash` install from `main` is unpinned and unsigned.
  - Adopting it may conflict with "not adopting a new web framework this year".
  - MIT is fine under our license rules.

NEXT ACTION: The operator decides whether a trial is worth it.
- **Owner:** operator.
- **Done when:** the decision is recorded. The operator first checks how many CI minutes the docs build uses today.
- **If approved:** run the trial with `telemetry = false` in `fastdocs.toml` before the first run, and pin the install script to a specific commit.
- **Stop condition:** stop if the docs build is under about 5% of CI minutes, or if any outbound request to stats.fastdocs.example.test shows up.
- **Hand-off:** none.

CONFIDENCE: medium. The load-bearing claim is confirmed and the context file is present. Three things limit it:
- I worked from a saved snapshot only, with no commit sha.
- I don't know our current docs builder or its CI cost.
- I can't verify whether the opt-out actually stops all network calls.

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "data_to_new_party",
  "item": {"type": "repo", "identity": "example-org/fastdocs@main (no sha captured; MIT, 1500 stars, last push 2026-10-02, not archived; snapshot 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "Build your docs site in milliseconds", "evidence": "tagline only; no benchmark, method or comparison in the snapshot",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "fastdocs builds docs really fast (sender)", "evidence": "restates the item's tagline; no evidence offered",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "telemetry is on by default and sends project name and file list to stats.fastdocs.example.test",
     "evidence": "snapshot fastdocs.toml: 'telemetry = true # sends project name and file list ... set to false to opt out'",
     "status": "CONFIRMED"},
    {"claim": "license is MIT", "evidence": "snapshot and meta.json both state MIT", "status": "CONFIRMED",
     "load_bearing": false},
    {"claim": "install is curl | bash from the main branch", "evidence": "snapshot Install section: curl -sSL .../fastdocs/main/install.sh | bash",
     "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found; at most goal 2 (cut CI minutes) if the docs build is a meaningful share of CI time, which the context file does not say",
          "overlap": "current docs builder not named in the context file; lychee already covers goal 1 and fastdocs does not address it",
          "burden": "new build tool, migration to fastdocs.toml, keeping telemetry disabled in every project",
          "risks": ["telemetry on by default sends file names to a new third party",
                    "unpinned curl | bash install from main",
                    "may conflict with 'not adopting a new web framework this year'",
                    "MIT license is acceptable"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated in snapshot", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether to allow a trial, after checking the docs build's share of CI minutes; if approved, set telemetry = false before first run and pin the install script to a commit",
                  "owner": "operator", "done_when": "decision recorded with the docs build's current CI-minute share",
                  "stop_condition": "stop if the docs build is under about 5% of CI minutes or any request to stats.fastdocs.example.test is observed",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```