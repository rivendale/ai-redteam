VERDICT: skip. None of our four goals is about database speed, and the "10x over SQLAlchemy" claim rests only on a chart image with no script or data behind it. Swapping the db layer on that basis would be a large migration for an unmeasured gain.

WHAT IT IS: example-org/speedy-orm on GitHub, default branch `main`. It is MIT licensed, has 2,200 stars, was last pushed and released on 2026-08-30, and is not archived. I read a saved snapshot (snapshot.md and meta.json, captured 2026-10-08), not the live repo. No commit sha was recorded.

CLAIMS CHECKED:
- **"10x faster than SQLAlchemy"** (the item's claim and the sender's framing). The only evidence is `docs/chart.png`. The snapshot says the benchmark script and data are not in the repository. There is no study design, no workload, no queries, no dataset size, no driver or database, and no SQLAlchemy version or mode (Core or ORM, 1.x or 2.x). What we would need is a script we can rerun on our own queries against PostgreSQL and SQLite. Nothing in the item shows the claim is false, so it is **UNVERIFIED**, not REFUTED. **The verdict rests on this claim.**
- **"MIT license."** Confirmed by meta.json and the README. This fits our license rule for anything we ship. **CONFIRMED**, not load-bearing.
- **Maintained (release 2026-08-30, not archived).** **CONFIRMED** by meta.json, not load-bearing. The 2,200 stars are popularity, not evidence that it works.

FIT:
- **Goal:** none found. The goals are dead links, CI minutes, semantic search of notes and an automatic changelog. None of them is about query speed or the db layer.
- **Overlap:** we already run PostgreSQL and SQLite (with sqlite-vec). The context file does not say SQLAlchemy is in use. The request implies it, and the operator should confirm. If SQLAlchemy is in use, this would replace a working layer rather than fill a gap.
- **Burden:** rewriting models and queries, migrations, and tests. We would also need to check that it supports sqlite-vec queries.
- **Cost:** free, open source, MIT (read from the snapshot, 2026-10-08).
- **Risks:**
  - The benchmark cannot be reproduced.
  - The project is young-looking, with its health judged only from stars and recent pushes.
  - Swapping an ORM leads to lock-in.
  - Postgres and sqlite-vec support is unknown.
  - The snapshot does not show whether there is telemetry.

NEXT ACTION: The operator replies to the sender that this is a skip. If db speed is a real pain point, the first step is to add it as a goal with a measured baseline, such as the slowest queries and their timings. Changing ORMs is not the first step.
- **Owner:** operator.
- **Done when:** the sender has the answer, and the baseline is either recorded as a goal or dropped.
- **Hand-off:** none.

CONFIDENCE: medium. The snapshot resolves the item and a context file is present. Confidence is limited because the load-bearing speed claim is UNVERIFIED, I worked from a saved copy with no commit sha, and the context file does not say whether SQLAlchemy is in use.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo", "identity": "example-org/speedy-orm@main (sha not recorded; MIT, 2200 stars, last push 2026-08-30, not archived; snapshot 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "10x faster than SQLAlchemy", "evidence": "README chart image only; benchmark script and data not in the repository; no workload, database or SQLAlchemy version given", "status": "UNVERIFIED"},
    {"claim": "MIT license", "evidence": "meta.json license field and README", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "actively maintained", "evidence": "meta.json: last push 2026-08-30, not archived", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (no goal concerns database performance)",
          "overlap": "PostgreSQL and SQLite with sqlite-vec already in use; SQLAlchemy implied by the request but not listed in the context file",
          "burden": "rewrite of models, queries, migrations and tests; sqlite-vec support unknown",
          "risks": ["benchmark not reproducible", "ORM lock-in", "PostgreSQL/sqlite-vec support unverified", "telemetry not checked in snapshot"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Tell the sender it is a skip; if db speed matters, record it as a goal with a measured baseline of our slowest queries first",
                  "owner": "operator", "done_when": "sender has the answer and the baseline goal is recorded or dropped",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```