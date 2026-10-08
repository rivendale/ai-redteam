```
VERDICT: skip. The 10x claim has no evidence behind it (a chart image, no script or data), and replacing the DB layer serves none of our four goals.
WHAT IT IS: example-org/speedy-orm, a GitHub repo. Read from a saved snapshot captured 2026-10-08, not live. MIT
  license, 2,200 stars, last push and last release 2026-08-30, not archived, default branch main. No commit sha was
  recorded in the snapshot.
CLAIMS CHECKED:
  - "10x faster than SQLAlchemy" (the README, repeated in the sender's words). Evidence: one chart, shipped as an
    image (docs/chart.png). The benchmark script and data are not in the repo. There is no workload, query mix,
    dataset size, database backend, SQLAlchemy version or mode (Core or ORM, sync or async), hardware or run count.
    Nothing can be checked or reproduced. A different workload, backend or SQLAlchemy configuration could change the
    result entirely. Status: UNVERIFIED. The verdict rests on this claim.
  - "MIT licensed". Evidence: meta.json and the snapshot agree. Status: CONFIRMED. Not load-bearing.
  - The 2,200 stars are popularity, not evidence of speed or reliability. They are not counted as support.
FIT:
  - Goal: none found. The context lists docs links, CI minutes, semantic search of notes, and the changelog. None of
    them is about ORM or query speed. It could only touch goal 2 (CI minutes) if DB-bound tests are a CI
    bottleneck, and nothing shows that they are.
  - Overlap: the context lists PostgreSQL and SQLite (with sqlite-vec) but names no ORM. The sender implies we use
    SQLAlchemy, but the context file does not list it. Whatever DB layer we have today already does this job.
  - Burden: high. Swapping the DB layer means rewriting models and queries, redoing migrations, and checking that it
    still works with sqlite-vec. It also adds a dependency we would have to keep up with.
  - Cost: free, open source, MIT (read 2026-10-08 from the snapshot). No tiers or terms found.
  - Risks: MIT passes our license rules for shipped or vendored code. Project health is fine but short-run: the last
    push was about 5 weeks before capture and the repo is not archived. Lock-in comes from an ORM rewrite. The
    install path and telemetry were not visible in the snapshot.
NEXT ACTION: The operator tells the sender: skip for now. We would reconsider only if (a) the project publishes a
  reproducible benchmark (script and data) for a workload like ours on PostgreSQL or SQLite, and (b) we can show that
  DB access is a real bottleneck for one of our goals. Owner: operator. Done when the sender has the answer and the
  two conditions. Hand-off: none.
CONFIDENCE: medium. The item is resolved from a saved snapshot and a context file is present. Confidence is limited
  because the load-bearing speed claim is UNVERIFIED, and the context does not say which DB layer we use today.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo",
           "identity": "example-org/speedy-orm@main (no sha recorded; MIT, 2200 stars, last push 2026-08-30, not archived; saved snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "10x faster than SQLAlchemy",
     "evidence": "README chart image only; benchmark script and data not in the repo; no workload, backend, versions or hardware given",
     "status": "UNVERIFIED"},
    {"claim": "MIT licensed",
     "evidence": "meta.json license field and snapshot text agree",
     "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (goals are dead links, CI minutes, semantic notes search, changelog)",
          "overlap": "our existing DB layer over PostgreSQL and SQLite already does this job; no ORM is listed in the context",
          "burden": "rewrite of models, queries and migrations; sqlite-vec compatibility to check; a new dependency to maintain",
          "risks": ["MIT, passes the license rules",
                    "last push 2026-08-30, not archived",
                    "lock-in from an ORM rewrite",
                    "install path and telemetry not visible in the snapshot"],
          "cost": {"price": "free", "tier": "open source", "limits": "none found", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Tell the sender: skip; reconsider only if a reproducible benchmark for our kind of workload is published and DB access is shown to be a bottleneck for one of our goals",
                  "owner": "operator",
                  "done_when": "the sender has the answer and the two conditions for reconsidering",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```