```
VERDICT: skip. Stars are not evidence, the project's own notice says its maintainers left in 2024 with no push since 2024-02-11, and "generate anything" maps to none of our four goals.
WHAT IT IS: example-org/megagen (repo, default branch main), MIT, 41,000 stars, 912 open issues, not archived,
  last push and last release v3.1.0 on 2024-02-11. Read from the saved snapshot captured 2026-10-08 (work/snapshot.md,
  work/meta.json), not live; no commit sha was captured.
CLAIMS CHECKED:
  - "41k stars" (sender): meta.json shows 41,000. CONFIRMED. Not load-bearing.
  - "...so it must be good" (sender's inference): stars measure attention, not quality or fit. The snapshot offers no
    tests, benchmarks or usage evidence. UNVERIFIED. Not load-bearing.
  - "Generate anything" (README): no scope, method or examples in the snapshot. The roadmap it points to was not
    captured. UNVERIFIED. Not load-bearing.
  - "The original maintainers have moved on; issues may go unanswered" (README update, 2024-03): this is the item's own
    statement, and it matches meta.json (no push in about 2 years and 8 months, 912 open issues). CONFIRMED. Load-bearing.
  - Last release v3.1.0 on 2024-02-11 (README and meta.json agree). CONFIRMED. Load-bearing.
FIT:
  - Goal: none found. The snapshot never says what it generates. The closest goal would be goal 4 (weekly changelog),
    and nothing in the item points there.
  - Overlap: the changelog draft is already built by changelog.py (nightly cron). Nothing else in use is comparable,
    because the item's job is undefined.
  - Burden: an unmaintained dependency we would have to patch ourselves, with no upstream to fix bugs or security issues.
  - Cost: free, open source, MIT; no tier or limits; checked 2026-10-08 from the snapshot.
  - Risks: MIT passes our license rule. Project health is poor: maintainers left, issues go unanswered, and it is not
    archived, so it looks alive when it is not. Telemetry and install path were not examined, because the snapshot has
    no code. No instructions inside the item tried to direct the reader.
NEXT ACTION: Reply to the sender with "skip: unmaintained since 2024-02 and no goal it serves." Ask which of our four
  goals they had in mind; if they name one, assess a maintained tool for that goal.
  Owner: operator. Done-when: the sender has the reply, and has either named a goal or dropped the idea.
  Hand-off: none.
CONFIDENCE: medium. The item is resolved and the claims the verdict rests on are CONFIRMED, with a context file
  present. Two things limit it: the work is from a saved snapshot, not a live read, and the snapshot is so thin
  (no description, no roadmap, no code) that a goal match can only be ruled out from its silence. The maintenance
  finding alone would still support skip.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo",
           "identity": "example-org/megagen (MIT, 41,000 stars, 912 open issues, last push and release v3.1.0 2024-02-11, not archived; snapshot 2026-10-08, no sha captured)",
           "resolved": true},
  "claims": [
    {"claim": "41k stars", "evidence": "meta.json: stars 41000", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "so it must be good", "evidence": "stars are popularity, not evidence; snapshot offers no tests, benchmarks or usage evidence",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "Generate anything", "evidence": "README one-liner, no scope or examples; roadmap not captured",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the original maintainers have moved on; issues may go unanswered",
     "evidence": "README update notice (2024-03), consistent with meta.json last_push 2024-02-11 and 912 open issues",
     "status": "CONFIRMED"},
    {"claim": "last release v3.1.0 on 2024-02-11", "evidence": "README and meta.json last_push agree",
     "status": "CONFIRMED"}
  ],
  "fit": {"goal": "none found",
          "overlap": "changelog.py already builds the changelog draft; nothing else comparable because the item's job is undefined",
          "burden": "an unmaintained dependency we would have to patch ourselves",
          "risks": ["MIT, passes license rule", "unmaintained since 2024-02 with no maintainers, not archived",
                    "telemetry and install path not examined: snapshot has no code"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Reply to the sender with skip (unmaintained since 2024-02, no goal served) and ask which of our four goals they had in mind",
                  "owner": "operator",
                  "done_when": "the sender has the reply and has either named a goal or dropped the idea",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```