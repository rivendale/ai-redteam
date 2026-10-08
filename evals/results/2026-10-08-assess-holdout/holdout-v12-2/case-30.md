VERDICT: try. crashrank serves goal 2 directly: it merges near-duplicate crash groups and ranks the top five by players hit. It is free, Apache-2.0, a tool we only run, and per its README it sends nothing off the machine. But the merging that would actually cut the noise is only claimed in the README and not shown, so it earns a bounded trial, not adoption.

WHAT IT IS: example-org/crashrank (repo). I worked from a saved snapshot captured 2026-10-08 and did not resolve it live; I cannot open links in this session. Facts read at capture: Apache-2.0, 540 stars, last push 2026-09-19, not archived, default branch `main`. No commit SHA was captured. It is a single static binary distributed as release downloads with a published SHA-256. I read only the README text, not the source.

CLAIMS CHECKED:
- "Merges crash groups whose stacks differ only in line numbers or build IDs." Evidence: README statement only. No examples, tests or method are shown. UNVERIFIED. The verdict rests on this, because the merging is what would cut the noise.
- "Prints the five groups affecting the most players, with first version and share of players hit, as a markdown table." Evidence: README only. PROBABLE, since it is a plain description of the output. Not load-bearing.
- "Reads a file you give it, writes to stdout: no network requests" and "no telemetry." Evidence: README only; the source was not read. UNVERIFIED. The verdict rests on this, because the export contains player crash data and that data must not reach a new party.
- "Reads a Crashlytics crash export (JSON)." Evidence: README only. It does not say which export path or schema (console download or BigQuery export). UNVERIFIED. The verdict rests on this, because if we cannot produce that file, the tool is of no use to us.
- "Apache-2.0." Evidence: license field in meta.json and the README. CONFIRMED. Not load-bearing, since any license is allowed for a tool we run and never ship.
- "Maintained." Evidence: last push 2026-09-19 and not archived, per meta.json. CONFIRMED. Not load-bearing.
- 540 stars is a true count. It is not evidence that the tool works.

FIT:
- Goal: goal 2, "Cut crash-report noise so the top five crashes are the ones worth fixing." The sender's guess is correct.
- Overlap: Firebase Crashlytics, already in use, ranks issues by users affected in its console. crashrank adds value only if its merging of groups split by line numbers or build IDs changes that top five. It does not replace Crashlytics; it reads Crashlytics' output, so the decision that Firebase stays is untouched.
- Burden: one binary to download and checksum, plus a manual export each week before triage. It needs no account and no new service.
- Cost: free, open source, Apache-2.0, read 2026-10-08 from the snapshot. No tiers or terms beyond the license.
- Risks: the README does not list platform builds, so macOS and Windows binaries are unconfirmed. The no-network claim is unverified. The install path is reasonable (a pinned release plus SHA-256, not `curl | bash`). It is a single-maintainer org of unknown health beyond the recent push. Lock-in is low.

NEXT ACTION: The operator downloads the release binary for macOS, verifies its SHA-256, and runs it on last week's Crashlytics export with networking blocked. They then compare its top five with the console's top five by users affected.
- Done when: both lists sit side by side, and each difference is explained as a real merge or an error.
- Stop condition: stop if the tool cannot read an export we can produce, if it tries any network access, or if its top five matches the console's in two consecutive weeks.
- Hand-off: none.

CONFIDENCE: medium. The context file is present and the fit is clear. But I worked from a saved README snapshot without the source, so the load-bearing merging, no-network and export-format claims are all UNVERIFIED.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/crashrank (branch main, no sha captured; Apache-2.0, 540 stars, last push 2026-09-19, not archived; read from snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "merges crash groups whose stacks differ only in line numbers or build IDs",
     "evidence": "README statement only; no examples, tests or method shown", "status": "UNVERIFIED"},
    {"claim": "prints the top five groups by players affected with first version and share as a markdown table",
     "evidence": "README description of output", "status": "PROBABLE", "load_bearing": false},
    {"claim": "reads a local file and writes to stdout with no network requests and no telemetry",
     "evidence": "README statement only; source not read", "status": "UNVERIFIED"},
    {"claim": "reads a Crashlytics crash export (JSON)",
     "evidence": "README only; which export path or schema is not stated", "status": "UNVERIFIED"},
    {"claim": "licensed Apache-2.0",
     "evidence": "meta.json license field and README", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "actively maintained",
     "evidence": "meta.json: last push 2026-09-19, not archived", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 2: cut crash-report noise so the top five crashes are the ones worth fixing",
          "overlap": "Firebase Crashlytics console already ranks issues by users affected; crashrank adds value only through its merging of near-duplicate groups",
          "burden": "one checksummed binary plus a manual Crashlytics export before each weekly triage; no account or service",
          "risks": ["no-network claim unverified (export holds player crash data)",
                    "macOS/Windows binaries not confirmed in README",
                    "Apache-2.0 tool we run, not ship: allowed",
                    "install is pinned release with SHA-256, not curl|bash"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "Apache-2.0",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Download the macOS release binary, verify its SHA-256, run it with networking blocked on last week's Crashlytics export, and compare its top five with the console's top five by users affected",
                  "owner": "operator",
                  "done_when": "both top-five lists are side by side and each difference is explained as a real merge or an error",
                  "stop_condition": "stop if it cannot read an export we can produce, attempts any network access, or its top five matches the console's in two consecutive weeks",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```