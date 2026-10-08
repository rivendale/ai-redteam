```
VERDICT: try. It fills a real gap for goal 1 by turning the lychee JSON we already produce into a readable dead-link table in the job summary, at no cost and with no new account. Its no-network claim rests only on its README, so read the source before relying on it.
WHAT IT IS: example-org/lychee-report (repo; no commit sha in the snapshot), MIT, 410 stars, last push and release 2026-09-12, not archived, default branch main, PyPI version 0.4.2. Read from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live.
CLAIMS CHECKED:
  - "Reads lychee's JSON and prints a markdown table of dead links grouped by page for the GitHub job summary": the README gives a usage line, but the snapshot has no source or sample output. PROBABLE. The verdict rests on this.
  - "Pure Python, standard library only; reads stdin, writes stdout, makes no network requests; no telemetry": this is the README's own description, and no source was captured. UNVERIFIED. The verdict rests on this because it runs in CI on every push.
  - "License: MIT": meta.json, read live at capture. CONFIRMED. The verdict rests on this.
  - "Last release 2026-09-12": meta.json last_push. CONFIRMED. The verdict does not rest on this.
  - "410 stars": meta.json. CONFIRMED as a count, but popularity is not evidence of quality. The verdict does not rest on this.
  - Sender's "we run lychee on every push": the context file lists lychee running on every push. CONFIRMED. The verdict rests on this.
FIT:
  Goal: goal 1 (keep the docs site free of dead links). It makes lychee's results readable where people already look, but it finds no new dead links.
  Overlap: lychee already does the checking, and this tool only formats lychee's output. It adds nothing new as a checker. Lychee may already have a built-in markdown output (`--format markdown`). That comes from my memory, not from the item, so the trial checks it.
  Burden: one pip install, pinned to 0.4.2, plus one pipe in the existing lychee CI step. No account, no service, and little upkeep beyond following lychee's JSON format.
  Cost: free, open source, MIT, no limits stated (checked 2026-10-08 from the snapshot).
  Risks: MIT meets the license rules even if vendored. The install comes from PyPI, so pin the version. The no-network and no-telemetry claims are unverified. If lychee changes its JSON format, the tool could break. The project is a single small repo, active as of September 2026.
NEXT ACTION: Operator reads the 0.4.2 source to confirm it uses only the standard library and makes no network calls, then adds `lychee --format json docs/ | lychee-report >> $GITHUB_STEP_SUMMARY` to the lychee job on one branch and compares the result with lychee's own `--format markdown` output. Done when one CI run shows the grouped table in the job summary next to the built-in output. Stop if the source makes any network call or imports a non-stdlib package, or if lychee's built-in markdown is already as useful. Hand-off: none.
CONFIDENCE: medium. The item and context file are present, but this is a saved snapshot with no source code, so the no-network claim is unverified, and the overlap with lychee's built-in markdown output is unchecked.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo", "identity": "example-org/lychee-report (no sha in snapshot; MIT, 410 stars, last push 2026-09-12, not archived, default branch main, PyPI 0.4.2; snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "reads lychee's JSON and prints a markdown table of dead links grouped by page for the GitHub job summary",
     "evidence": "README usage line only; no source or sample output in the snapshot", "status": "PROBABLE"},
    {"claim": "pure Python, standard library only, no network requests, no telemetry",
     "evidence": "README self-description only; source not captured", "status": "UNVERIFIED"},
    {"claim": "license is MIT", "evidence": "meta.json, read live at capture", "status": "CONFIRMED"},
    {"claim": "last release 2026-09-12", "evidence": "meta.json last_push", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "410 stars", "evidence": "meta.json; popularity is not evidence of quality", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "we run lychee on every push (sender)", "evidence": "context file, tools already in use", "status": "CONFIRMED"}
  ],
  "fit": {"goal": "keep the docs site free of dead links (goal 1): makes lychee's results readable in the job summary",
          "overlap": "lychee already does the checking; this only formats its output; lychee may already have a built-in markdown format (from memory, not from the item; to be checked)",
          "burden": "one pinned pip install and one pipe in the existing lychee CI step",
          "risks": ["MIT, fits the license rules even if vendored", "no-network and no-telemetry claims unverified (no source in snapshot)", "PyPI dependency; pin to 0.4.2", "breaks if lychee's JSON format changes"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Read the 0.4.2 source to confirm stdlib-only and no network calls, then pipe lychee's JSON through it in the lychee CI job on one branch and compare with lychee's own markdown output",
                  "owner": "operator",
                  "done_when": "one CI run shows the grouped table in the job summary next to the built-in output",
                  "stop_condition": "stop if the source makes any network call or imports a non-stdlib package, or if lychee's built-in markdown output is already as useful",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```