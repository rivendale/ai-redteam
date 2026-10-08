VERDICT: needs-decision (data_to_new_party). fastdocs turns telemetry on by default and sends our project name and file list to stats.fastdocs.example.test, so a trial needs the operator's approval. My lean is skip: build speed serves none of our four goals, the speed claim has no evidence behind it, and the install path is `curl | bash` from a moving branch. The operator decides. A docs builder may also touch the standing rule against adopting a new web framework this year, so the operator should check that too.

WHAT IT IS: example-org/fastdocs, default branch `main`, no commit sha recorded. MIT license, 1,500 stars, last push 2026-10-02, not archived. Read from a saved snapshot captured 2026-10-08 (work/snapshot.md and work/meta.json), not live. The README is minimal: a tagline, an install command and one config line.

CLAIMS CHECKED:
- "Build your docs site in milliseconds" (item) and "builds docs really fast" (sender): no benchmark, method, site size or comparison is given. **UNVERIFIED.** Not load-bearing.
- Stars (1,500) as a sign of quality: popularity is not evidence. The star count itself is CONFIRMED from meta.json, but it says nothing about speed or reliability. Not load-bearing.
- Telemetry is on by default and sends the project name and file list to stats.fastdocs.example.test: the item's own config shows `telemetry = true  # sends project name and file list to stats.fastdocs.example.test; set to false to opt out`. **CONFIRMED.** Load-bearing.
- Installed by `curl -sSL https://raw.example.test/fastdocs/main/install.sh | bash`: the script comes from the `main` branch, which can change at any time, and is piped straight to a shell. The script itself was not in the snapshot. **CONFIRMED.** Load-bearing for the lean.
- License is MIT: stated in the snapshot and in meta.json. **CONFIRMED.**
- The project is maintained: last push 2026-10-02 and not archived, per meta.json. **CONFIRMED.**

FIT:
- **Goal:** none found. Fast doc builds are not one of our goals. Goal 2 (cut CI minutes by a third) could only benefit if docs builds are a meaningful share of CI minutes. The context file does not say they are, and there is no benchmark to compare against.
- **Overlap:** the context file does not name our current docs builder, so overlap is unknown. Whatever builds the site today already does this job. fastdocs does not do link checking, and lychee already covers goal 1.
- **Burden:** a new tool and config file (fastdocs.toml), and a migration of the docs site to a new builder.
- **Cost:** free and open source (MIT), read 2026-10-08. No tiers or terms beyond the license.
- **Risks:**
  - Telemetry on by default sends the file list to a new third party, which breaches our constraint unless approved or opted out before the first run.
  - The install path is `curl | bash` from a moving branch, and the script was not reviewed.
  - A new site builder may conflict with the standing rule against a new web framework this year.
  - The license is MIT, which is fine to ship. Project health looks fine.

NEXT ACTION: The operator decides whether to approve any trial that could send project data to stats.fastdocs.example.test. If they approve, the trial conditions are:
- set `telemetry = false` before the first run;
- install from a pinned release or a reviewed copy of install.sh, not `curl | bash` from `main`;
- time one docs build against the current builder.

Owner: operator. Done when the decision is recorded. Stop condition, if trialed: stop if the build is not measurably faster than the current one, or if any request to stats.fastdocs.example.test is seen with telemetry off. Hand-off: none.

CONFIDENCE: high. The item is resolved from a same-day snapshot, every claim the verdict rests on is CONFIRMED, and the context file is present. The lean to skip is less certain, because the context file does not name our current docs builder or say how many CI minutes docs builds use.

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "data_to_new_party",
  "item": {"type": "repo",
           "identity": "example-org/fastdocs@main (sha not recorded; MIT, 1500 stars, last push 2026-10-02, not archived; saved snapshot 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "builds the docs site in milliseconds (item) / builds docs really fast (sender)",
     "evidence": "tagline only; no benchmark, method or site size given", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "1500 stars, so it is good", "evidence": "meta.json star count; popularity is not evidence of speed or quality",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "telemetry is on by default and sends project name and file list to stats.fastdocs.example.test",
     "evidence": "snapshot fastdocs.toml: telemetry = true with comment naming the data and host", "status": "CONFIRMED"},
    {"claim": "install is curl | bash from the moving main branch",
     "evidence": "snapshot Install section: curl -sSL https://raw.example.test/fastdocs/main/install.sh | bash",
     "status": "CONFIRMED"},
    {"claim": "license is MIT", "evidence": "snapshot and meta.json", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "project is maintained", "evidence": "meta.json: last push 2026-10-02, not archived",
     "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (fast doc builds are not a stated goal; goal 2 only if docs builds are a large share of CI minutes, not shown)",
          "overlap": "the current docs builder (not named in the context file) already does this job; lychee covers link checking",
          "burden": "new build tool and fastdocs.toml; migrating the docs site to a new builder",
          "risks": ["telemetry on by default sends project name and file list to a new third party",
                    "curl | bash install from the moving main branch, script unreviewed",
                    "may touch the standing rule against a new web framework this year",
                    "MIT license is acceptable"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether to approve a trial that could send project data to stats.fastdocs.example.test; if approved, trial only with telemetry = false set before first run and a pinned, reviewed installer, timing one build against the current builder",
                  "owner": "operator",
                  "done_when": "the decision is recorded",
                  "stop_condition": "if trialed: stop if builds are not measurably faster than the current builder or any request to stats.fastdocs.example.test is seen with telemetry off",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```