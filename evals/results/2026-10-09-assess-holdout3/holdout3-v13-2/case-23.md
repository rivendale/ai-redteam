```
VERDICT: needs-decision (standing_rule): tracklabs would serve goal 3 (a transcript with every episode), but it is SSPL-1.0, not Apache-2.0 as the summary said, and our license rule names no SSPL case even for tools we run on our own machines; it also sends telemetry by default, contrary to the summary. Do not install it until the host decides.
WHAT IT IS: example-org/tracklabs (repo; commit sha not captured), default branch main, license SSPL-1.0, 980 stars, last push and last release 2026-09-26, not archived. Read from a saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not live.
CLAIMS CHECKED:
  - "Apache-2.0" (research agent): REFUTED. meta.json and the README both say SSPL-1.0, and the README adds: "Offering the software as a hosted service requires releasing your whole service stack under the SSPL." Load-bearing.
  - "No telemetry" (research agent): REFUTED. The README says "anonymous usage reports and the audio file's duration and language are sent to the project's servers unless you set `TRACKLABS_TELEMETRY=off`." Telemetry is on by default. Load-bearing.
  - "Transcribes audio" (split from the next claim): CONFIRMED. The README says it "Transcribes audio to text and chapters." Load-bearing.
  - "...locally" (inference): UNVERIFIED. The snapshot never says where transcription runs. The telemetry list (duration and language, not audio) hints that it is local, but nothing settles it. Load-bearing, because uploading episode audio would change the fit.
  - "Works offline" (research agent): UNVERIFIED. The snapshot says neither way. Default telemetry shows that it contacts the project's servers, but not whether it needs them. Not load-bearing.
  - "Recommend installing" (research agent): this is a recommendation, not a fact. The two facts given for it are refuted above.
FIT:
  - Goal: goal 3, a transcript with every episode. Chapters might also help show notes, which is not a listed goal.
  - Overlap: none found. Nothing in use transcribes. Reaper, ffmpeg (loudness.py only), Buzzsprout, Mailchimp, Google Docs and Hugo do other jobs.
  - Burden: one local tool to install and maintain on the Mac mini, a transcription step for each weekly 45-minute episode, and the telemetry environment variable to set and keep set.
  - Cost: no price stated in the snapshot; it appears to be free open-source software. No tiers or limits were stated. Terms are SSPL-1.0. Read from the snapshot dated 2026-10-09.
  - Risks:
    - License: the rule allows MIT, Apache-2.0 or BSD for site code, and GPL or AGPL only for tools on our own machines. SSPL is in neither list. It may only be run locally and must never ship on the site or be offered as a hosted service.
    - Telemetry: on by default, sending usage data, episode duration and language to the project's servers. This is not listener or subscriber data, but it does leave the machine unless turned off.
    - Mac support: not stated in the snapshot.
    - Install path: not shown in the snapshot.
    - Health: maintained (pushed 13 days before capture), moderate popularity.
    - No text in the snapshot tries to direct the reader.
NEXT ACTION: The host decides whether an SSPL-1.0 tool may run on our own machines, either by extending the license rule or by declining. If yes, the operator must set TRACKLABS_TELEMETRY=off and confirm, from its docs, both that transcription is local and that it runs on macOS before any trial. Owner: host. Done when the host has recorded yes or no on SSPL for local tools. Hand-off: none.
CONFIDENCE: medium. The context file is present and the license and telemetry facts are clear in the item's own text. Two things limit it: I worked from a saved snapshot rather than a live read, and whether transcription is local (load-bearing) and whether it supports macOS are both unverified.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "standing_rule",
  "item": {"type": "repo",
           "identity": "example-org/tracklabs (main, sha not captured; SSPL-1.0, 980 stars, last push 2026-09-26, not archived; snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "licensed Apache-2.0 (research agent)", "evidence": "meta.json and README: SSPL-1.0, hosted-service clause", "status": "REFUTED"},
    {"claim": "no telemetry (research agent)", "evidence": "README: usage reports, audio duration and language sent to project servers unless TRACKLABS_TELEMETRY=off", "status": "REFUTED"},
    {"claim": "transcribes audio to text", "evidence": "README: 'Transcribes audio to text and chapters'", "status": "CONFIRMED"},
    {"claim": "transcription runs locally", "evidence": "snapshot does not say where transcription runs; telemetry list omits audio, which only hints at local processing", "status": "UNVERIFIED"},
    {"claim": "works offline (research agent)", "evidence": "snapshot says nothing either way; default telemetry contacts project servers", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "publish a transcript with every episode (goal 3)",
          "overlap": "none found: nothing in use transcribes",
          "burden": "one local tool on the Mac mini, a transcription step per weekly episode, keeping telemetry off",
          "risks": ["SSPL-1.0 is outside the license rule (MIT/Apache-2.0/BSD for site code; GPL/AGPL only for local tools)",
                    "telemetry on by default sends usage, episode duration and language to the project",
                    "macOS support and install path not stated in the snapshot"],
          "cost": {"price": "none stated (open source)", "tier": "open source", "limits": "none stated",
                   "terms": "SSPL-1.0", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Host decides whether an SSPL-1.0 tool may run on our own machines; if yes, operator sets TRACKLABS_TELEMETRY=off and confirms local transcription and macOS support before any trial",
                  "owner": "host", "done_when": "the host has recorded yes or no on SSPL for local tools",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```