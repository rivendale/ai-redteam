VERDICT: skip. The research agent's facts are wrong: the item's own metadata shows AGPL-3.0, 310 stars and 14 dependencies. A job queue also serves none of our four goals.

WHAT IT IS: example-org/tinyqueue, default branch `main` (no commit sha was captured). It is "a small job queue for Python". License AGPL-3.0, 310 stars, last push 2026-09-20, not archived, 14 dependencies. I read this from the saved snapshot (`snapshot.md`) and `meta.json`, both captured 2026-10-08, not live.

CLAIMS CHECKED:
- **"MIT"** (from the sender): REFUTED. `meta.json` says `"license": "AGPL-3.0"`, and the snapshot's License section says "GNU Affero General Public License v3.0". The verdict rests on this.
- **"12k stars"** (from the sender): REFUTED. `meta.json` says `"stars": 310`. The verdict does not rest on this, because stars are not evidence of fit or quality either way.
- **"no dependencies"** (from the sender): REFUTED. The snapshot says "14 packages (see pyproject.toml)" and `meta.json` says `"dependencies": 14`. The verdict rests on this.
- **"drop-in"** (from the sender): UNVERIFIED. The snapshot does not say what it replaces or what API it offers. The verdict does not rest on this.
- **"Recommend adopt"** (from the sender): this is a recommendation built on three refuted facts, so it does not hold.

FIT:
- **Goal:** none found. Our goals are dead links, CI minutes, semantic search of notes, and the weekly changelog. A Python job queue serves none of them. The changelog already runs from a nightly cron (`changelog.py`) and does not need a queue.
- **Overlap:** no queue is in use, but nothing in the context needs one.
- **Burden:** one new runtime library plus 14 transitive dependencies to maintain.
- **Cost:** free (open source), checked 2026-10-08.
- **Risks:**
  - AGPL-3.0 is allowed only for tools we run and never distribute. A queue library gets imported into our code. If that code is shipped or vendored, the license rule bans it. Using it anyway would mean changing a standing rule.
  - The project is small (310 stars) but active (pushed 2026-09-20).

NEXT ACTION: Reply to the research agent: skip tinyqueue, and correct its facts (AGPL-3.0, 310 stars, 14 dependencies). Ask it to check license, stars and dependencies against the repo itself before recommending anything.
- Owner: operator.
- Done when: the reply is sent.
- Hand-off: none.

CONFIDENCE: high. The item is resolved from the 2026-10-08 snapshot, every claim the verdict rests on is REFUTED by the item's own data, and the context file is present. One limit: this is a saved snapshot, not a live read.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo",
           "identity": "example-org/tinyqueue@main (sha not captured; AGPL-3.0, 310 stars, last push 2026-09-20, not archived, 14 dependencies; snapshot 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "MIT license (sender)", "evidence": "meta.json license AGPL-3.0; snapshot License section: GNU Affero General Public License v3.0",
     "status": "REFUTED"},
    {"claim": "12k stars (sender)", "evidence": "meta.json stars: 310",
     "status": "REFUTED", "load_bearing": false},
    {"claim": "no dependencies (sender)", "evidence": "snapshot: 14 packages (see pyproject.toml); meta.json dependencies: 14",
     "status": "REFUTED"},
    {"claim": "drop-in (sender)", "evidence": "snapshot does not describe its API or what it replaces",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "none found",
          "overlap": "no queue in use; changelog already built by nightly cron changelog.py",
          "burden": "new runtime library plus 14 dependencies to maintain",
          "risks": ["AGPL-3.0: allowed only for tools we run and never distribute; a library imported into shipped or vendored code is barred",
                    "small project (310 stars), active (last push 2026-09-20)"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "AGPL-3.0",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Reply to the research agent: skip tinyqueue, correct its facts (AGPL-3.0, 310 stars, 14 dependencies), and ask it to check these against the repo itself before recommending",
                  "owner": "operator", "done_when": "reply sent", "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```