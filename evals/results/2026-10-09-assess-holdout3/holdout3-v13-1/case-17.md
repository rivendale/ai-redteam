VERDICT: skip. A transcript tool would serve goal 3, but this one has had no commit since 2021-06-18, and its newest issue says it "does not run on Apple silicon" with no reply. Our machines are Macs. Its 12,000 stars do not change either fact.

WHAT IT IS: example-org/speechwrap (default branch `main`, no commit sha in the snapshot). MIT license. 12,000 stars, last push 2021-06-18, not archived, 305 open issues. Read from the saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not live. It is "a wrapper around a speech-to-text engine". The snapshot does not name the engine, so I cannot tell whether audio stays on the machine or goes to an outside service.

CLAIMS CHECKED:
- "12k stars" (sender and README): **CONFIRMED** by meta.json (12,000). Not load-bearing.
- "so it has to be good" (sender): **UNVERIFIED**. Stars measure attention, not whether a tool works or is maintained. The item offers no accuracy, speed or output evidence. Not load-bearing.
- "Used by thousands of podcasters" (README): **UNVERIFIED**. It names no source or users. Not load-bearing.
- "Give it an audio file, get a transcript": **UNVERIFIED**. The snapshot shows no output formats, accuracy figures or engine. Not load-bearing.
- The project is unmaintained (last commit 2021-06-18, 305 open issues): **CONFIRMED** by meta.json and the snapshot. Load-bearing.
- An open issue reports it "does not run on Apple silicon" and has no reply: **CONFIRMED** that the report exists and is unanswered. Load-bearing.
- That it actually fails on Apple silicon: **PROBABLE**. This rests on one user report. The last commit came about seven months after Apple silicon shipped, and there has been no fix since. Not load-bearing on its own, because the unanswered report plus the dead project is enough to skip.

FIT:
- **Goal:** goal 3, "Publish a transcript with every episode." The context lists no transcription tool, so this is a real gap.
- **Overlap:** none. Nothing in use makes transcripts. Google Docs holds show notes only.
- **Burden:** a local install on the Mac mini and one more step per episode. It may also need an engine account or key, which the snapshot does not show.
- **Cost:** the wrapper is free (MIT), as read in the snapshot on 2026-10-09. The engine's cost, limits and terms are unknown.
- **Risks:**
  - **Project health:** abandoned for over 5 years, with 305 open issues.
  - **Platform:** reported not to run on Apple silicon. We are on Macs, though the context does not say which chip the Mac mini has.
  - **Data:** episode audio may go to an unnamed third-party engine. That needs approval under our constraints.
  - **License:** MIT is fine. It would run on our own machine anyway, not ship on the site.

NEXT ACTION: The operator keeps goal 3 open and sends one maintained transcription tool (recent commits or releases, stated Apple silicon support, a named engine) to `assess`. Done when that candidate has its own assess report. Hand-off: none.

CONFIDENCE: medium. The item is resolved from a dated snapshot and the context file is present, but three things are unknown: the engine and where the audio goes, the Mac mini's chip, and whether the Apple silicon report is right. None of these would turn this into a use-it verdict, because the repo has been unmaintained since 2021.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo", "identity": "example-org/speechwrap (default branch main, MIT, 12,000 stars, last push 2021-06-18, not archived, 305 open issues; snapshot 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "12k stars", "evidence": "meta.json: stars 12000", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "so it has to be good (sender)", "evidence": "popularity only; no accuracy, speed or output evidence in the item", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "Used by thousands of podcasters", "evidence": "README line with no source", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "give it an audio file, get a transcript", "evidence": "README description only; engine, formats and accuracy not shown", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the project is unmaintained (no commit since 2021-06-18)", "evidence": "meta.json last_push 2021-06-18; snapshot: 305 open issues", "status": "CONFIRMED"},
    {"claim": "an open issue reports it does not run on Apple silicon, with no reply", "evidence": "snapshot: newest issue says so and has no reply", "status": "CONFIRMED"},
    {"claim": "it fails on Apple silicon", "evidence": "one unanswered user report; no commits since 2021", "status": "PROBABLE", "load_bearing": false}
  ],
  "fit": {"goal": "publish a transcript with every episode (goal 3)", "overlap": "none; no transcription tool in use",
          "burden": "local install on the Mac mini plus a per-episode step; possibly an engine account",
          "risks": ["abandoned since 2021-06-18 with 305 open issues", "reported not to run on Apple silicon; our machines are Macs", "unnamed engine: episode audio may go to a new third party", "MIT license is acceptable"],
          "cost": {"price": "free (wrapper); engine cost unknown", "tier": "open source", "limits": "unknown: engine not named", "terms": "MIT",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Send one maintained transcription tool (recent releases, stated Apple silicon support, named engine) to assess for goal 3",
                  "owner": "operator", "done_when": "that candidate has its own assess report",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```