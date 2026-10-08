```
VERDICT: skip. It does the same job as lychee, which already runs on every push, and nothing in the item shows it is faster or better, so switching would add churn without serving a goal.
WHAT IT IS: example-org/deadlink-scan (repo; no commit sha in the snapshot), MIT, 2,300 stars, last push 2026-09-30, not archived, default branch main, last release v1.4.2 (2026-09-18). Read from the saved snapshot and meta.json captured 2026-10-08, not live.
CLAIMS CHECKED:
  - "fast" (the sender's word and the README's): no benchmark, timing, or comparison is given. UNVERIFIED. The verdict rests on this: speed is the only thing that could justify replacing lychee (for goal 2, cutting CI minutes), and nothing supports it.
  - Checks markdown files for dead links (walks files, follows links, prints failures): the item's own description of its function; no docs or source in the snapshot. PROBABLE. The verdict rests on this, because it is what makes it overlap with lychee.
  - Single static binary: stated in the README, with no release assets or build details shown. PROBABLE, not load-bearing.
  - Runs in CI and supports GitHub Actions: stated, but no action or workflow example is shown. PROBABLE, not load-bearing.
  - License MIT: the README and meta.json agree. CONFIRMED, not load-bearing.
  - "Checking links by hand does not scale": a motivation, not a claim about this tool. Not load-bearing.
FIT:
  - Goal: goal 1 (docs free of dead links), but that goal is already served by lychee. Goal 2 (CI minutes) only if it were measurably faster than lychee, which is not shown.
  - Overlap: full overlap with lychee, which runs on every push.
  - Burden: a new CI job or a migration off lychee, plus a second tool to maintain.
  - Cost: free and open source (MIT) as of 2026-10-08.
  - Risks: MIT fits our license rules even for vendoring. The install path is not documented in the snapshot. Telemetry and network behavior beyond the checked links are unknown (no source was read). Health looks active (push 2026-09-30).
NEXT ACTION: None needed. Keep lychee. The operator owns this, and it is done when the link is closed. If CI minutes from link checking become a real cost, revisit this item only with a published benchmark against lychee. Hand-off: none.
CONFIDENCE: medium. Limited because the snapshot is a short README excerpt, not the live repo or its source, and the speed claim is unverified. The context file is present.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo",
           "identity": "example-org/deadlink-scan (no sha in snapshot; MIT, 2300 stars, last push 2026-09-30, not archived, default branch main, release v1.4.2 2026-09-18; snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "it is fast", "evidence": "README says 'fast'; no benchmark, timing or comparison given", "status": "UNVERIFIED"},
    {"claim": "checks markdown files for dead links (walks files, follows links, prints failures)", "evidence": "README description of its function; no docs or source in snapshot", "status": "PROBABLE"},
    {"claim": "single static binary", "evidence": "README statement; no release assets shown", "status": "PROBABLE", "load_bearing": false},
    {"claim": "runs in CI and supports GitHub Actions", "evidence": "README statement; no action or workflow example shown", "status": "PROBABLE", "load_bearing": false},
    {"claim": "license is MIT", "evidence": "README and meta.json agree", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "keep the docs free of dead links (goal 1), already served by lychee; goal 2 (CI minutes) only if faster than lychee, which is not shown",
          "overlap": "lychee already does link checking on every push",
          "burden": "new CI job or migration off lychee, plus a second tool to maintain",
          "risks": ["MIT, compatible with license rules", "install path not documented in snapshot", "telemetry and network behavior unknown (source not read)"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Keep lychee and close the link; revisit only if a published benchmark shows it beats lychee on CI time",
                  "owner": "operator", "done_when": "the link is closed with this verdict recorded",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```