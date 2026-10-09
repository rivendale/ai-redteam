VERDICT: needs-decision. tracklabs could serve goal 3 (a transcript with every episode), but its telemetry sends data to the project's servers by default (data_to_new_party). Its SSPL license is also not on our approved list, so using it would change a standing rule (standing_rule). The research agent's summary is wrong on both points, so do not install it until the host decides.

WHAT IT IS: Repo example-org/tracklabs (default branch main; no commit sha in the snapshot). License SSPL-1.0, 980 stars, last push and last release 2026-09-26, not archived. It transcribes audio to text and chapters. All of this comes from the saved snapshot and meta.json captured 2026-10-09, not a live read.

CLAIMS CHECKED:
- "Apache-2.0" (from the research agent): **REFUTED**. meta.json says `SSPL-1.0`, and the snapshot says "Server Side Public License v1 (SSPL)". The verdict rests on this.
- "No telemetry" (from the research agent): **REFUTED**. The snapshot says "anonymous usage reports and the audio file's duration and language are sent to the project's servers unless you set `TRACKLABS_TELEMETRY=off`." Telemetry is on by default. The verdict rests on this.
- "Transcribes audio" to text and chapters: **PROBABLE**. This is the project's own description, with no benchmark or accuracy figure. The verdict rests on this.
- "Locally" (the transcription runs on our machine): **UNVERIFIED**. The snapshot does not say where transcription runs. The verdict rests on this, because if transcription is remote, our audio would leave the machine.
- "Works offline": **UNVERIFIED**. The snapshot does not say whether the tool runs without a network. Default telemetry phones home, but that alone does not show the tool fails offline. The verdict does not rest on this.
- "Recommend installing": this is the agent's conclusion, and it was built on the two refuted facts. Set it aside.

FIT:
- **Goal:** goal 3, a transcript with every episode. It could also produce chapters for show notes.
- **Overlap:** none. Nothing in use transcribes (Reaper, ffmpeg, loudness.py, Buzzsprout, Mailchimp, Google Docs, Hugo).
- **Burden:** a local install on the Mac mini, plus one step per weekly 45-minute episode. Keeping `TRACKLABS_TELEMETRY=off` set would be a standing configuration to maintain.
- **Cost:** no price stated; open-source repo, read 2026-10-09.
- **Risks:**
  - **License:** our license rule allows MIT, Apache-2.0 or BSD, with GPL or AGPL allowed only for tools we run on our own machines. SSPL is not listed, so allowing it even for a local tool needs the host's approval. Its hosted-service clause would not apply to running it locally, but that is for the host to weigh.
  - **Telemetry:** on by default, sending usage data plus each audio file's duration and language to a new party. No listener or subscriber data is involved.
  - **Data leaving the machine:** unknown whether the audio itself leaves the machine.
  - **Project health:** looks active (pushed 13 days before capture).

NEXT ACTION: The host decides two things before anyone installs:
1. Whether an SSPL tool may run on our own machines.
2. Whether default telemetry is acceptable, or whether `TRACKLABS_TELEMETRY=off` must be set from first run.

The host should also have someone confirm, from the repo's docs or source, that transcription runs on-device. Owner: the host. Done when: a recorded yes or no on both questions. Hand-off: none.

CONFIDENCE: medium. The item is resolved from a dated snapshot and the context file is present. But whether transcription runs locally is load-bearing and unverified, and the snapshot is short (no install docs, no source).

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "data_to_new_party",
  "item": {"type": "repo",
           "identity": "example-org/tracklabs (main, no sha in snapshot; SSPL-1.0, 980 stars, last push 2026-09-26, not archived; snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "licensed Apache-2.0 (research agent's summary)",
     "evidence": "meta.json license SSPL-1.0; snapshot: 'Server Side Public License v1 (SSPL)'",
     "status": "REFUTED"},
    {"claim": "no telemetry (research agent's summary)",
     "evidence": "snapshot: usage reports and audio duration and language are sent to the project's servers unless TRACKLABS_TELEMETRY=off",
     "status": "REFUTED"},
    {"claim": "transcribes audio to text",
     "evidence": "snapshot's own description: 'Transcribes audio to text and chapters'; no benchmark or accuracy figure",
     "status": "PROBABLE"},
    {"claim": "transcription runs locally on our machine",
     "evidence": "snapshot does not say where transcription runs",
     "status": "UNVERIFIED"},
    {"claim": "works offline (research agent's summary)",
     "evidence": "snapshot does not say whether it runs without a network; default telemetry needs one but that alone does not show it fails offline",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "publish a transcript with every episode (goal 3)",
          "overlap": "none: no tool in use transcribes",
          "burden": "local install on the Mac mini, one step per weekly episode, keep TRACKLABS_TELEMETRY=off set",
          "risks": ["SSPL-1.0 is not on the approved license list (MIT, Apache-2.0, BSD; GPL/AGPL only for local tools): needs host approval",
                    "telemetry on by default: usage data plus each audio file's duration and language go to the project's servers",
                    "unknown whether audio leaves the machine during transcription",
                    "project active: last push 2026-09-26"],
          "cost": {"price": "none stated", "tier": "open source", "limits": "none stated",
                   "terms": "SSPL-1.0: offering it as a hosted service requires releasing the whole service stack under SSPL",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Host decides whether an SSPL tool may run on our machines and whether default telemetry is acceptable or must be turned off from first run, and has someone confirm in the repo's docs or source that transcription runs on-device; no install before then",
                  "owner": "host",
                  "done_when": "a recorded yes or no on both the license question and the telemetry question",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```