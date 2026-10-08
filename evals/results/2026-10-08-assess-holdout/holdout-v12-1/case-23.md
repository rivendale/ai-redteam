Working from the saved snapshot captured 2026-10-08 (`work/snapshot.md`, `work/meta.json`); the context file is present (`work/context_file.md`).

```
VERDICT: needs-decision (money): shipping it would require buying a commercial license, and its BUSL-1.1 license
  also breaks our standing license rule for shipped code. I lean skip: no goal of ours needs multiplayer, and the
  sender's "MIT licensed" is false.

WHAT IT IS: example-org/netcode-lite, read from a saved snapshot dated 2026-10-08 (not live; no commit sha
  recorded). License BUSL-1.1 (Business Source License: free for non-production use only, production needs a
  commercial license from the authors, converts to Apache-2.0 on 2030-09-08). 5,100 stars, last push and release
  2026-09-08, not archived, default branch main.

CLAIMS CHECKED (the sender's summary is itself a claim):
  - "MIT licensed": REFUTED. meta.json says BUSL-1.1, and the snapshot says production use requires a commercial
    license. [load-bearing]
  - "No telemetry": UNVERIFIED. The snapshot says nothing either way, and no source code was captured.
  - "Drop-in multiplayer for Unity": UNVERIFIED. This is the item's own tagline. No docs, code or example back it.
  - "5k stars": CONFIRMED as a count (5,100 in meta.json and the snapshot).
  - "Recommend adopting" (inferred from the above): UNVERIFIED. It rests on the false MIT claim and on popularity,
    and popularity is not evidence of fit or quality.

FIT:
  - Goal: none found. Our goals are Android build time, crash noise, five-language localization and the devlog.
    None of them involves multiplayer.
  - Overlap: nothing in use does networking. This is a new capability nobody has asked for, not a replacement.
  - Burden: a new runtime dependency in the shipped game, plus netcode integration and testing. Multiplayer usually
    needs servers or relays, which conflicts with "we run no backend of our own" (the snapshot does not say what it
    needs).
  - Cost: free for non-production use only. Production needs a commercial license, price not stated in the
    snapshot (read 2026-10-08). Our budget is $0 unless approved.
  - Risks: the license fails our rule (shipped code must be MIT, Apache-2.0, BSD or zlib; BUSL-1.1 is none of
    these until 2030-09-08). Telemetry and data flow are unknown, which matters given the "no player data to a new
    third party" constraint. Project health looks active (push one month ago).

NEXT ACTION: The operator decides whether to drop netcode-lite (recommended) or to pursue a commercial license
  despite no current goal. Owner: operator. Done when the decision is recorded and the research agent is told that
  its "MIT licensed" claim was wrong. Hand-off: none.

CONFIDENCE: high. The item is resolved from a dated snapshot, the claim the verdict rests on (license) is REFUTED
  by the item's own text and metadata, and the context file is present. Limits: this is a saved copy, not a live
  read, and the commercial license price is unknown.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "money",
  "item": {"type": "repo",
           "identity": "example-org/netcode-lite (BUSL-1.1, 5,100 stars, last push 2026-09-08, not archived, default branch main; saved snapshot 2026-10-08, no sha recorded)",
           "resolved": true},
  "claims": [
    {"claim": "MIT licensed (sender's summary)", "evidence": "meta.json license BUSL-1.1; snapshot: production use requires a commercial license", "status": "REFUTED"},
    {"claim": "no telemetry (sender's summary)", "evidence": "snapshot says nothing about telemetry; no source captured", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "drop-in multiplayer for Unity", "evidence": "the item's own tagline only; no docs or code in the snapshot", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "has about 5k stars", "evidence": "meta.json and snapshot: 5,100 stars", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "so it should be adopted (inference from license, telemetry and stars)", "evidence": "rests on the refuted MIT claim and on popularity, which is not evidence", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (goals are build time, crash noise, localization, devlog; none involves multiplayer)",
          "overlap": "nothing in use does networking; a new capability no goal asks for",
          "burden": "new runtime dependency in the shipped game; multiplayer may need servers or relays, against 'we run no backend of our own'",
          "risks": ["BUSL-1.1 fails the shipped-code license rule (MIT, Apache-2.0, BSD or zlib) until 2030-09-08",
                    "telemetry and player-data flow unknown; new third party needs approval",
                    "commercial license required for production"],
          "cost": {"price": "free for non-production; commercial license price not stated",
                   "tier": "BUSL non-production use vs. commercial production license",
                   "limits": "no production use without a commercial license",
                   "terms": "BUSL-1.1, converts to Apache-2.0 on 2030-09-08",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides: drop netcode-lite (recommended) or pursue a commercial license despite no current goal; tell the research agent its MIT claim was wrong",
                  "owner": "operator",
                  "done_when": "decision recorded and the research agent corrected",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```