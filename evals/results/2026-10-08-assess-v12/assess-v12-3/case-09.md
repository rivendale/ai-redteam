```
VERDICT: needs-decision (data_to_new_party). fastdocs sends your project name and file list to stats.fastdocs.example.test by default, so the operator must approve before anyone tries it. My lean is skip for now: no goal names docs build speed, and its only speed claim has no evidence behind it.

WHAT IT IS: example-org/fastdocs, default branch main (commit sha not captured). MIT license. 1,500 stars, last push 2026-10-02, not archived. Read from a saved snapshot (work/snapshot.md and meta.json, captured 2026-10-08), not live.

CLAIMS CHECKED:
- "Build your docs site in milliseconds" (README tagline), and the sender's "builds docs really fast": UNVERIFIED. The snapshot has no benchmark, site size, hardware or comparison, and 1,500 stars is not evidence. Not load-bearing.
- Telemetry is on by default and sends the project name and file list to stats.fastdocs.example.test (fastdocs.toml: `telemetry = true # ... set to false to opt out`): CONFIRMED by the project's own config docs. Load-bearing: file lists are company data going to a new third party.
- Licensed MIT (meta.json and snapshot agree): CONFIRMED. Not load-bearing.
- Install is `curl -sSL https://raw.example.test/fastdocs/main/install.sh | bash`: CONFIRMED as the documented path. This pipes a script from a moving branch straight into a shell, with no pin or signature. A risk, but not what the verdict rests on.

FIT:
- Goal: none found directly. Docs build speed is not a listed goal. It could serve goal 2 (cut CI minutes by a third) only if the docs build is a real share of CI minutes, and nothing shows that yet.
- Overlap: the context file does not say what builds the docs site today, so overlap is unknown. It does not touch link checking (lychee already covers goal 1).
- Burden: a new build tool, a fastdocs.toml, a migration of the docs build, and keeping it updated.
- Cost: free and open source (MIT), as read 2026-10-08. No paid tier appears in the snapshot.
- Risks:
  - Telemetry on by default sends data to a new party.
  - The curl | bash install pulls from main.
  - MIT is compatible with our license rule.
  - Project looks active (pushed 6 days before capture).
  - Swapping the docs generator may be close to "not adopting a new web framework this year". The operator should confirm it does not fall under that.

NEXT ACTION: The operator decides whether a trial is allowed.
- If no: the item becomes watch, revisited if the docs build turns out to be a large share of CI minutes.
- If yes: the trial runs with `telemetry = false` set before the first build, from a pinned release rather than curl | bash on main. It first measures how many CI minutes the current docs build uses.
- Owner: operator. Done when the decision is recorded. Hand-off: none.

CONFIDENCE: high for the needs-decision verdict, which rests on the project's own confirmed telemetry default, with the item resolved and a context file present. Limits: this is a saved snapshot with no commit sha, and the current docs generator and its CI cost are unknown, so the skip lean is less certain than the verdict.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "data_to_new_party",
  "item": {"type": "repo",
           "identity": "example-org/fastdocs@main (sha not captured; MIT, 1500 stars, last push 2026-10-02, not archived; snapshot 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "builds the docs site in milliseconds / really fast (README and sender)",
     "evidence": "tagline only; no benchmark, site size or method given", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "telemetry is on by default and sends project name and file list to stats.fastdocs.example.test",
     "evidence": "its own fastdocs.toml docs: telemetry = true, opt out by setting false", "status": "CONFIRMED"},
    {"claim": "licensed MIT", "evidence": "meta.json license field and snapshot both say MIT", "status": "CONFIRMED",
     "load_bearing": false},
    {"claim": "installed via curl | bash from the main branch",
     "evidence": "snapshot Install section: curl -sSL .../fastdocs/main/install.sh | bash", "status": "CONFIRMED",
     "load_bearing": false}
  ],
  "fit": {"goal": "none found directly; possibly goal 2 (cut CI minutes) only if the docs build is a large share of CI time, which is not shown",
          "overlap": "unknown: context file does not name the current docs generator; does not overlap lychee (goal 1)",
          "burden": "new build tool, fastdocs.toml, docs build migration, upkeep",
          "risks": ["telemetry on by default sends project name and file list to a new third party",
                    "curl | bash install from moving main branch, unpinned and unsigned",
                    "MIT license is compatible with our license rule",
                    "replacing the docs generator may touch the 'no new web framework this year' decision"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether a fastdocs trial is allowed; if yes, only with telemetry = false from a pinned release, after measuring the current docs build's CI minutes",
                  "owner": "operator", "done_when": "the decision is recorded",
                  "stop_condition": "if a trial is approved, stop if the docs build saves under a meaningful share of CI minutes or any request to stats.fastdocs.example.test is seen",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```