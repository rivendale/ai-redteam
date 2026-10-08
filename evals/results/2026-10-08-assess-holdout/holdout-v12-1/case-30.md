```
VERDICT: try. It targets goal 2 directly, runs locally against a Crashlytics export we already have access to, and costs nothing, but its noise-merging and no-network claims rest only on the README, so a one-export trial should settle them before it joins weekly triage.
WHAT IT IS: example-org/crashrank (repo; no commit sha in the snapshot), default branch main, Apache-2.0, 540 stars, last push and last release 2026-09-19, not archived. Read from the saved snapshot and meta.json captured 2026-10-08, not live.
CLAIMS CHECKED:
  - "Reads a Crashlytics crash export (JSON) and prints the five groups affecting the most players, with first version seen and share of players hit, as a markdown table" (README and the sender's words): the README describes it specifically, but no source, sample output or tests were captured. PROBABLE. Verdict rests on this.
  - "Merges crash groups whose stacks differ only in line numbers or build IDs": this is the part that would cut noise. The README asserts it with no method, examples or tests. UNVERIFIED. Verdict rests on this, and the trial tests it.
  - "No network requests, no telemetry; reads a file and writes to stdout": the README asserts it, and no source was read. UNVERIFIED. Verdict rests on this, because crash exports can carry player data and our rule bars sending it to a new third party.
  - "Apache-2.0, last release 2026-09-19": matches meta.json. CONFIRMED. Not load-bearing.
  - "540 stars": a true count per meta.json, CONFIRMED. It is not evidence of quality and is not load-bearing.
FIT:
  - Goal: goal 2 ("cut crash-report noise so the top five crashes are the ones worth fixing").
  - Overlap: Firebase Crashlytics already groups crashes and ranks top issues. crashrank adds value only if its re-merging (line numbers, build IDs) changes that top five. Nothing else in use does this post-processing.
  - Burden: one binary to download and check against its SHA-256, plus a weekly export step. The snapshot does not say how to produce the "Crashlytics crash export (JSON)", and that step is the main unknown. No accounts, no services.
  - Cost: free, open source, no tiers. Terms are Apache-2.0, checked 2026-10-08 from the snapshot.
  - Risks: license is fine (Apache-2.0, a tool we run and never ship). It ships as a release binary with a published SHA-256; the snapshot does not list which OSes the binary targets, and we need macOS and/or Windows. The no-network claim is unverified, and the export holds player data. Project health looks active (release 19 days before capture), with a single maintainer org of unknown size.
NEXT ACTION: The operator runs crashrank on one week's Crashlytics export on the Mac mini with networking blocked or monitored, then compares its top five with the Crashlytics console's top five for the same week. Done when both lists are side by side and every difference is explained (a merged group, or a different rank). Stop if any of these happens: it makes any network connection, its top five match Crashlytics' own top five with no merges, there is no macOS or Windows binary, or no way to produce the JSON export is found. Hand-off: none.
CONFIDENCE: medium. The item is a saved snapshot with no source read, and the two load-bearing behavior claims (merging, no network) are UNVERIFIED. The context file is present.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo", "identity": "example-org/crashrank (default branch main, Apache-2.0, last push 2026-09-19, not archived; snapshot 2026-10-08, no sha captured)",
           "resolved": true},
  "claims": [
    {"claim": "reads a Crashlytics JSON export and prints the five crash groups affecting the most players, with first version and share of players, as a markdown table", "evidence": "README description only; no source, sample output or tests in the snapshot", "status": "PROBABLE"},
    {"claim": "merges crash groups whose stacks differ only in line numbers or build IDs", "evidence": "README assertion; no method, examples or tests", "status": "UNVERIFIED"},
    {"claim": "no network requests and no telemetry; reads a file and writes to stdout", "evidence": "README assertion; source not read", "status": "UNVERIFIED"},
    {"claim": "licensed Apache-2.0, last release 2026-09-19", "evidence": "README matches meta.json captured 2026-10-08", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "540 stars", "evidence": "meta.json captured 2026-10-08; a count, not evidence of quality", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 2: cut crash-report noise so the top five crashes are the ones worth fixing",
          "overlap": "Firebase Crashlytics already groups and ranks crashes; crashrank only adds value if its re-merging changes the top five",
          "burden": "one checksum-verified binary plus a weekly export step whose method the snapshot does not describe",
          "risks": ["no-network claim unverified while exports hold player data", "supported OSes for the binary not listed (we need macOS/Windows)", "Apache-2.0 is fine for a tool we run and never ship"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "Apache-2.0",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Run crashrank on one week's Crashlytics export on the Mac mini with networking blocked or monitored, and compare its top five with the Crashlytics console's top five for that week",
                  "owner": "operator", "done_when": "both lists are side by side and every difference is explained",
                  "stop_condition": "stop if it makes any network connection, finds no merges and matches Crashlytics' top five, has no macOS/Windows binary, or no way to produce the JSON export is found",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```