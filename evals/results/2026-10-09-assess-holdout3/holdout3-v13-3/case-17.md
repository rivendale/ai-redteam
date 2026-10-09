VERDICT: watch. It would serve goal 3 (a transcript with every episode), and nothing we use does that job today. But the repo has had no commit since 2021-06-18, its newest issue says it "does not run on Apple silicon" with no reply, and the snapshot does not say which engine it wraps, so it is not something to run on our Macs now. 12,000 stars do not change that.

WHAT IT IS: example-org/speechwrap, default branch `main` (no commit sha in the snapshot). MIT license. 12,000 stars, 305 open issues, last push 2021-06-18 (more than five years before capture), not archived. All of this was read from the saved snapshot and meta.json captured 2026-10-09, not live. It describes itself as "a wrapper around a speech-to-text engine: give it an audio file, get a transcript." The snapshot does not name the engine.

CLAIMS CHECKED:
- "12k stars" (sender): the repo has 12,000 stars per meta.json. **CONFIRMED.** Not load-bearing.
- "so it has to be good" (sender's inference from the stars): popularity is not evidence of quality, and the item offers no accuracy figures, benchmarks or method. Nothing in it settles this. **UNVERIFIED.** Not load-bearing.
- "Used by thousands of podcasters" (README): no source, list or data is given. **UNVERIFIED.** Not load-bearing.
- The project is still maintained: last commit 2021-06-18, 305 open issues, and the newest issue has no reply. **REFUTED** by its own metadata. Load-bearing.
- It runs on our Macs: the newest issue reports "does not run on Apple silicon" and nobody has answered. The snapshot cannot settle it, and we don't know which chip the Mac mini has. **UNVERIFIED.** Load-bearing.

FIT:
- **Goal:** goal 3, "Publish a transcript with every episode."
- **Overlap:** none. Reaper, ffmpeg (used only by loudness.py), Buzzsprout, Mailchimp, Google Docs and Hugo do not transcribe.
- **Burden:** a local install of an unmaintained tool plus whatever engine it wraps. That engine might need its own model download, an API key or an account. For a weekly 45-minute episode, someone would also have to correct each transcript.
- **Cost:** the wrapper is free under MIT. The engine's cost and terms are unknown. If it is a paid cloud API, it needs the host's approval and breaks the $0 budget. Read from the 2026-10-09 snapshot.
- **Risks:**
  - License: MIT is fine for anything, including a tool on our own machines.
  - Platform: there is an unanswered report that it fails on Apple silicon, and our machines are Macs.
  - Project health: nothing has been pushed in five years and 305 issues are open.
  - Data: unknown whether audio leaves the machine. The audio is our own, not listener data, so the third-party rule is not triggered, but a cloud engine could still need a new account.

NEXT ACTION: The operator checks the Mac mini's chip (Apple menu > About This Mac).
- If it is Apple silicon, this repo stays off the list until a commit lands that fixes Apple silicon support.
- If it is Intel, re-assess once we know which engine speechwrap wraps and where it sends the audio.
- Done when the chip is recorded next to this report.
- Hand-off: none.

CONFIDENCE: medium.
- The snapshot is resolved and the context file is present.
- Two things limit it. The load-bearing Apple-silicon claim is UNVERIFIED, and the snapshot does not name the wrapped engine, so cost, accounts and where audio goes are unknown.
- Everything was read from a saved copy dated 2026-10-09, not live.

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "repo", "identity": "example-org/speechwrap (main, no sha in snapshot; MIT, 12,000 stars, 305 open issues, last push 2021-06-18, not archived; read from snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "the repo has 12,000 stars", "evidence": "meta.json: stars 12000", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "12k stars, so it has to be good", "evidence": "popularity only; no accuracy figures, benchmark or method in the item", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "Used by thousands of podcasters", "evidence": "README line, no source or data", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the project is maintained", "evidence": "last commit 2021-06-18, 305 open issues, newest issue unanswered", "status": "REFUTED"},
    {"claim": "it runs on our Macs", "evidence": "newest issue: 'does not run on Apple silicon', no reply; Mac mini chip not stated in context", "status": "UNVERIFIED"}
  ],
  "fit": {"goal": "publish a transcript with every episode (goal 3)",
          "overlap": "none: no tool in use transcribes",
          "burden": "local install of an unmaintained wrapper plus its unnamed engine (possible model download, API key or account), and hand-correcting each weekly 45-minute transcript",
          "risks": ["unanswered report that it does not run on Apple silicon; our machines are Macs",
                    "no commit since 2021-06-18, 305 open issues",
                    "wrapped engine not named: unknown whether audio leaves the machine or needs a paid account",
                    "MIT license, acceptable"],
          "cost": {"price": "free (wrapper); engine cost unknown", "tier": "open source", "limits": "unknown for the wrapped engine",
                   "terms": "MIT", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Check which chip the Mac mini has; if Apple silicon, keep speechwrap off the list until a commit fixes Apple silicon support; if Intel, re-assess once the wrapped engine and where it sends audio are known",
                  "owner": "operator", "done_when": "the Mac mini's chip is recorded next to this report",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```