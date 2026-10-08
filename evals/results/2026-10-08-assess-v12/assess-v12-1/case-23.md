VERDICT: skip. tinyqueue serves none of our four goals, and the research agent's three facts are each contradicted by the item itself: it is AGPL-3.0 rather than MIT, it has 310 stars rather than 12k, and it has 14 dependencies rather than none. So "adopt" does not hold.

WHAT IT IS: example-org/tinyqueue on the default branch `main` (no commit sha in the snapshot). It is "a small job queue for Python." License AGPL-3.0, 310 stars, last push 2026-09-20, not archived, 14 dependencies. I read this from the saved snapshot (work/snapshot.md and meta.json) captured 2026-10-08, not live.

CLAIMS CHECKED (the claims are the research agent's summary; the item itself makes no performance claims):
- "MIT": the evidence offered is the agent's word. The snapshot says "GNU Affero General Public License v3.0" and meta.json says `"license": "AGPL-3.0"`. **REFUTED.** The verdict rests on this.
- "12k stars": the evidence offered is the agent's word. meta.json says `"stars": 310`. **REFUTED.** The verdict does not rest on this. Popularity would not be evidence of usefulness anyway.
- "no dependencies": the evidence offered is the agent's word. The snapshot says "14 packages (see pyproject.toml)" and meta.json says `"dependencies": 14`. **REFUTED.** The verdict rests on this.
- "drop-in": nothing is offered and nothing in the snapshot settles it. We also have no queue for it to drop into. **UNVERIFIED.** The verdict does not rest on this.
- "Recommend adopt": this is the agent's conclusion, and it is built on the three refuted facts above.

FIT:
- **Goal:** none found. A job queue does not serve dead-link checking, CI minutes, semantic search or the changelog.
- **Overlap:** no job queue is in use and none is needed. The changelog already runs as a nightly cron script (changelog.py).
- **Burden:** one new library plus 14 transitive dependencies to track.
- **Cost:** free, open source, AGPL-3.0, checked 2026-10-08 from the snapshot.
- **Risks:**
  - The license breaks our rules. We allow AGPL only for tools we run and never distribute. A Python queue library gets imported into code we ship, which would need MIT, Apache-2.0 or BSD.
  - The agent's summary was wrong on every checkable fact. Its other forwarded recommendations deserve a second look.

NEXT ACTION: The operator tells the research agent the recommendation is rejected and gives the three refuted facts (AGPL-3.0, 310 stars, 14 dependencies). Done when the agent's recommendation is withdrawn or corrected. Hand-off: none.

CONFIDENCE: high. The item is resolved from a dated snapshot, the claims the verdict rests on are REFUTED by the item's own license and metadata, and the context file is present. The only limit is that I read a saved copy rather than the live repo.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo",
           "identity": "example-org/tinyqueue@main (AGPL-3.0, 310 stars, 14 dependencies, last push 2026-09-20, not archived; read from saved snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "MIT license", "evidence": "snapshot.md: 'GNU Affero General Public License v3.0'; meta.json license AGPL-3.0",
     "status": "REFUTED"},
    {"claim": "12k stars", "evidence": "meta.json stars: 310", "status": "REFUTED", "load_bearing": false},
    {"claim": "no dependencies", "evidence": "snapshot.md: '14 packages (see pyproject.toml)'; meta.json dependencies: 14",
     "status": "REFUTED"},
    {"claim": "drop-in", "evidence": "nothing in the snapshot addresses it", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "none found", "overlap": "no job queue in use or needed; changelog already runs via nightly cron (changelog.py)",
          "burden": "one new library plus 14 transitive dependencies",
          "risks": ["AGPL-3.0 violates license rule for code we ship (MIT/Apache-2.0/BSD only)",
                    "research agent's summary was wrong on every checkable fact"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "AGPL-3.0",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Tell the research agent the adopt recommendation is rejected, citing AGPL-3.0, 310 stars and 14 dependencies",
                  "owner": "operator", "done_when": "the research agent's recommendation is withdrawn or corrected",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```