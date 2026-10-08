VERDICT: try. It targets goal 2 directly: it merges crash groups that differ only in line numbers or build IDs, which is the noise our Crashlytics top five suffers from. It is free, Apache-2.0 and claims to run locally. Every claim rests on its README, though, and it is unclear how we get the JSON export it reads, so it needs a bounded trial before we adopt it.

WHAT IT IS: example-org/crashrank, a GitHub repo on default branch `main`. It is Apache-2.0, has 540 stars, was last pushed 2026-09-19 and is not archived. These facts come from meta.json, read live at capture on 2026-10-08. I worked from the saved snapshot (snapshot.md, 2026-10-08), not the live page, and no commit SHA was recorded. It is a CLI that reads a Crashlytics crash export (JSON) and prints the top five crash groups as a markdown table. It ships as a single static binary with a published SHA-256. I read only the README text, not the source.

CLAIMS CHECKED:
- **Merges crash groups whose stacks differ only in line numbers or build IDs.** The only evidence is the README description, with no example output or code read. PROBABLE. **The verdict rests on this.**
- **Prints the five groups affecting the most players, with first version seen and share of players hit.** The only evidence is the README. PROBABLE. **The verdict rests on this.**
- **Makes no network requests and has no telemetry; reads a file and writes to stdout.** The only evidence is the README, and I did not read the source. PROBABLE. **The verdict rests on this**, because crash data contains player data and the context forbids sending it to a new party.
- **Apache-2.0.** The license field in meta.json, read live, confirms it. CONFIRMED. This is fine either way, since we run the tool and do not ship it.
- **Actively maintained.** meta.json shows the last push and release on 2026-09-19 and the repo is not archived. CONFIRMED as a fact about activity. The 540 stars are a true count, but they are not evidence that the tool works.
- **Runs on our machines (macOS or Windows).** The README only says "single static binary" and names no platforms. UNVERIFIED. The verdict does not rest on this, because triage can run on any machine.
- **Sender's framing, "goal 2?".** This is a fit question, answered below: yes, it plausibly serves goal 2.

FIT:
- **Goal:** Goal 2, "Cut crash-report noise so the top five crashes are the ones worth fixing." The tool's main feature is exactly that: dedupe near-identical groups, then rank by players affected.
- **Overlap:** Firebase Crashlytics, already in use, groups crashes itself and shows top issues in its console. Crashrank adds a second merge pass and a triage table on top of Crashlytics' own grouping, so it is a layer, not a replacement. It does not conflict with the decision that "Firebase stays our crash service".
- **Burden:**
  - We need a JSON export from Crashlytics each week. The README does not say how to produce one. If it means the Crashlytics-to-BigQuery export, that could add a Google Cloud billing setup, which would hit both the "no new account" and "$0 budget" constraints.
  - Beyond the export, the burden is one binary download and one command per triage. There is no new service.
- **Cost:** Free and open source, Apache-2.0, as of 2026-10-08. The tool has no tiers. Any cost would come from the export path, which is unknown.
- **Risks:**
  - The license is allowed under our rules.
  - The install path is a release binary checked against a published SHA-256, with no `curl | bash`.
  - The no-network and no-telemetry claims are README-only.
  - Platform builds are not listed.
  - Health looks fine: pushed 19 days before capture.

NEXT ACTION:
- **Action:** The operator, or whoever runs the weekly triage, gets one week's Crashlytics export, then downloads the release binary for their OS and verifies its SHA-256. They run crashrank on the export and compare its top five against the Crashlytics console's top issues for the same week.
- **Owner:** operator.
- **Done when:** both top-five lists are compared for one week, and each group crashrank merged or reranked has been checked by hand to see whether the merge was correct.
- **Stop condition:** stop if any of these is true:
  - Producing the export needs a new account, BigQuery billing or any paid service. That would make this a `needs-decision` for money or account, so bring it back.
  - No binary exists for macOS or Windows.
  - Its top five does not differ usefully from the console's.
  - It makes any network request.
- **Hand-off:** none. This is using a tool, not borrowing ideas.

CONFIDENCE: medium. The item is resolved from a dated snapshot and the context file is present. But every claim the verdict rests on is supported only by the README. I read no source and no sample output, and the export path is unknown.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo", "identity": "example-org/crashrank@main (Apache-2.0, 540 stars, last push 2026-09-19, not archived; snapshot 2026-10-08, no SHA recorded)", "resolved": true},
  "claims": [
    {"claim": "merges crash groups whose stacks differ only in line numbers or build IDs", "evidence": "README description only; no code or sample output read", "status": "PROBABLE"},
    {"claim": "prints the five groups affecting the most players, with first version and share of players hit", "evidence": "README description only", "status": "PROBABLE"},
    {"claim": "no network requests and no telemetry; reads a file, writes to stdout", "evidence": "README statement only; source not read", "status": "PROBABLE"},
    {"claim": "licensed Apache-2.0", "evidence": "meta.json license field read live at capture", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "actively maintained (last push 2026-09-19, not archived)", "evidence": "meta.json read live at capture; 540 stars is a count, not evidence of quality", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "runs on macOS or Windows", "evidence": "README says single static binary; platforms not named", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 2: cut crash-report noise so the top five crashes are the ones worth fixing", "overlap": "Firebase Crashlytics already groups crashes and lists top issues; crashrank adds a merge pass and triage table on top of it", "burden": "one binary download and one command per weekly triage, plus producing a JSON export whose source (possibly a BigQuery export) is not documented", "risks": ["Apache-2.0, allowed (tool run, not shipped)", "no-network and no-telemetry claims are README-only", "export path may require Google Cloud/BigQuery billing, a new account or cost", "supported platforms not listed", "install is a checksum-verified release binary, no curl | bash"], "cost": {"price": "free", "tier": "open source", "limits": "none stated; cost of producing the export unknown", "terms": "Apache-2.0", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Run crashrank on one week's Crashlytics export (checksum-verified release binary) and compare its top five with the Crashlytics console's top issues for the same week", "owner": "operator", "done_when": "both top-five lists compared for one week and every merged or reranked group checked by hand", "stop_condition": "stop if getting the export needs a new account or paid service (bring back as needs-decision), if no macOS/Windows binary exists, if its top five adds nothing over the console, or if it makes any network request", "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```