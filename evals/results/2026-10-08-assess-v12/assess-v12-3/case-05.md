VERDICT: skip. It does the same job as lychee, which already runs on every push, and it offers no evidence that it is faster, so another link-check job would only add CI minutes against goal 2.

WHAT IT IS: example-org/deadlink-scan on GitHub, read from a saved snapshot captured 2026-10-08 (no commit sha recorded). License MIT, 2,300 stars, last push 2026-09-30, not archived, default branch `main`, last release v1.4.2 (2026-09-18). The project looks healthy and active.

CLAIMS CHECKED:
- **"Fast"** (in the README and in the sender's words): no benchmark, method or comparison is given. **UNVERIFIED.** Load-bearing: speed is the only thing that could make it better than lychee.
- **"Walks markdown files, follows each link, prints the ones that fail"**: this is the README's own description; no source was read. **PROBABLE.** Load-bearing: this is what makes it overlap with lychee.
- **"Single static binary"**: stated in the README; no build or release files were read. **PROBABLE.** Not load-bearing.
- **"Runs in CI / supports GitHub Actions"**: stated in the README; no Action or workflow file was shown. **PROBABLE.** Not load-bearing.
- **License MIT**: matches meta.json from the live read at capture. **CONFIRMED.** Not load-bearing.
- **"Checking links by hand does not scale"**: this is a motivation, not a claim about the tool. It doesn't apply here, since lychee already automates the check.

FIT:
- **Goal:** goal 1 (keep the docs free of dead links). That goal is already served.
- **Overlap:** lychee does the same job and runs on every push. This is full overlap.
- **Burden:** a new CI job or a lychee replacement, plus another tool to maintain.
- **Cost:** free and open source (MIT), read from the 2026-10-08 snapshot. No tiers or limits are mentioned.
- **Risks:**
  - The license is fine for any use under our rules.
  - The install path is unknown (release binary or Action, not shown).
  - Telemetry is not stated either way.
  - It contacts the link targets, as lychee already does.
  - Adding it alongside lychee works against goal 2 (cut CI minutes).

NEXT ACTION: Tell the sender we are keeping lychee. Revisit only if lychee becomes a measured CI-time problem; then a timed side-by-side on the docs folder would be the test.
- Owner: operator.
- Done when: the sender has the answer.
- Hand-off: none.

CONFIDENCE: medium. The verdict works from a saved snapshot, the speed claim is unverified, and its functional claims rest on README text rather than source.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo",
           "identity": "example-org/deadlink-scan (MIT, 2300 stars, last push 2026-09-30, not archived, default branch main, v1.4.2 2026-09-18; saved snapshot 2026-10-08, no sha recorded)",
           "resolved": true},
  "claims": [
    {"claim": "it is fast", "evidence": "README and sender assert it; no benchmark, method or comparison given",
     "status": "UNVERIFIED"},
    {"claim": "walks markdown files, follows each link and prints the failing ones", "evidence": "README description; source not read",
     "status": "PROBABLE"},
    {"claim": "single static binary", "evidence": "README statement; no release or build files read",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "runs in CI and supports GitHub Actions", "evidence": "README statement; no Action or workflow file shown",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "license is MIT", "evidence": "meta.json live read at capture matches README",
     "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "keep the docs site free of dead links (goal 1), already served by lychee",
          "overlap": "lychee does the same job and runs on every push",
          "burden": "a new CI job or a lychee replacement, plus another tool to maintain",
          "risks": ["adds CI minutes against goal 2 if run alongside lychee",
                    "install path and telemetry not stated in the snapshot",
                    "MIT license is acceptable under our rules"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Tell the sender we keep lychee; revisit only if lychee becomes a measured CI-time problem, then time both on the docs folder",
                  "owner": "operator", "done_when": "the sender has the answer", "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```