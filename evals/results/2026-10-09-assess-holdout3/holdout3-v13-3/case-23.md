VERDICT: needs-decision. It would serve goal 3 (a transcript with every episode), but its license is SSPL-1.0, which our license rule does not list for any use. Using it means changing a standing rule. Two of the research agent's claims are false: the license is not Apache-2.0, and telemetry is on by default.

WHAT IT IS: example-org/tracklabs, read from a saved snapshot captured 2026-10-09 (no commit sha recorded). It is a repo on default branch `main`, licensed SSPL-1.0 per meta.json and the README. It has 980 stars, was last pushed 2026-09-26 (last release the same day), and is not archived. It describes itself as a tool that "Transcribes audio to text and chapters." I did not install or run it.

CLAIMS CHECKED:
- **"Apache-2.0"** (research agent): REFUTED. meta.json and the README both say SSPL-1.0, and the README says hosting it as a service "requires releasing your whole service stack under the SSPL." *Load-bearing.*
- **"no telemetry"** (research agent): REFUTED. The README says "anonymous usage reports and the audio file's duration and language are sent to the project's servers unless you set `TRACKLABS_TELEMETRY=off`." So telemetry is on by default. *Load-bearing.*
- **"transcribes audio"**: CONFIRMED. This is the item's own description. *Load-bearing.*
- **"…locally"** (research agent): UNVERIFIED. The snapshot does not say where transcription happens or what model it uses. Not load-bearing for this verdict, but it matters for the decision: if audio leaves the machine, that is a new data flow.
- **"works offline"** (research agent): UNVERIFIED. Nothing in the snapshot settles it. Default telemetry shows it contacts the network, but not that it needs to. Not load-bearing.
- **"Recommend installing"** (research agent): this is a recommendation, not evidence. It rests on the two refuted claims above.

FIT:
- **Goal:** goal 3, a transcript with every episode. It might also help chapters and show notes.
- **Overlap:** none found. Nothing in use transcribes; ffmpeg is used only by loudness.py.
- **Burden:** a new local tool on the Mac mini, a weekly run per 45-minute episode, telemetry has to be switched off on every machine and run, and the output needs review.
- **Cost:** no price, tier or account requirement is stated in the snapshot (as read 2026-10-09). It is source-available under SSPL.
- **Risks:**
  - **License:** our rule allows MIT, Apache-2.0 or BSD for site code, and GPL or AGPL only for tools run on our own machines. SSPL is neither. Running it locally needs an approved exception, and it must never ship on the site.
  - **Telemetry:** on by default, sending usage plus each episode's duration and language to the project's servers. This is not listener data, but it is data leaving the machine unless `TRACKLABS_TELEMETRY=off` is set. Whether that switch stops everything is untested.
  - **Unknowns:** local versus cloud processing and the install path are not shown.
  - **Health:** looks active (pushed 13 days before capture).

NEXT ACTION: The host decides whether to allow an SSPL-licensed tool that runs only on our own machines, with telemetry forced off. Done when the decision is written into the "Constraints" or "Already decided" section of context_file.md. Do not install anything before that. If it is approved, a separate assess is still needed to confirm it transcribes locally and offline. Hand-off: none.

CONFIDENCE: medium. The item is resolved and the context file is present, and the load-bearing claims are CONFIRMED or REFUTED from the item's own text. But this is a thin saved snapshot rather than a live read. It does not show where transcription runs, what it costs, or how it installs, and those facts bear on the host's decision.

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "standing_rule",
  "item": {"type": "repo",
           "identity": "example-org/tracklabs (default branch main, SSPL-1.0, 980 stars, last push 2026-09-26, not archived; saved snapshot captured 2026-10-09, no sha recorded)",
           "resolved": true},
  "claims": [
    {"claim": "licensed Apache-2.0 (research agent)", "evidence": "meta.json and README: SSPL-1.0; hosting as a service requires releasing the whole service stack under SSPL", "status": "REFUTED"},
    {"claim": "no telemetry (research agent)", "evidence": "README: usage reports plus audio duration and language sent to the project's servers unless TRACKLABS_TELEMETRY=off", "status": "REFUTED"},
    {"claim": "transcribes audio to text", "evidence": "README: 'Transcribes audio to text and chapters'", "status": "CONFIRMED"},
    {"claim": "transcription runs locally (research agent)", "evidence": "snapshot does not say where transcription runs or which model it uses", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "works offline (research agent)", "evidence": "nothing in the snapshot settles it; default telemetry contacts the network but does not show it is required", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "publish a transcript with every episode (goal 3)",
          "overlap": "none found: nothing in use transcribes; ffmpeg is used only by loudness.py",
          "burden": "new local tool on the Mac mini, weekly run per episode, telemetry must be set off on every run, transcript review",
          "risks": ["SSPL-1.0 is not in our license rule (MIT/Apache-2.0/BSD, or GPL/AGPL for local tools only): needs an exception and must never ship on the site",
                    "telemetry on by default sends usage and each episode's duration and language to the project's servers",
                    "local versus cloud transcription and the install path are not shown in the snapshot"],
          "cost": {"price": "not stated in snapshot", "tier": "source-available, no tiers stated", "limits": "none stated",
                   "terms": "SSPL-1.0: offering it as a hosted service requires releasing the whole service stack under SSPL",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Host decides whether to allow an SSPL-licensed tool run only on our own machines with telemetry forced off; no install before that",
                  "owner": "host",
                  "done_when": "the decision is recorded in context_file.md under Constraints or Already decided",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```