**VERDICT:** try. It would serve goal 3 (a transcript with every episode), and nothing in use does that job. But the repo has had no commit since 2021-06-18, and its newest open issue says it does not run on Apple silicon. So it gets one bounded run on the Mac mini, not adoption.

**WHAT IT IS:** example-org/speechwrap, default branch `main` (no commit SHA in the snapshot). It is MIT licensed, has 12,000 stars, was last pushed 2021-06-18 (about 5 years 4 months before capture), is not archived, and has 305 open issues. It wraps an unnamed speech-to-text engine: you give it an audio file and get a transcript back. Everything here is read from a saved snapshot and meta.json captured 2026-10-09, not live.

**CLAIMS CHECKED:**
- **"12k stars"** (sender), CONFIRMED. meta.json shows 12,000.
- **"…so it has to be good"** (sender's inference), UNVERIFIED. Stars measure past attention, not quality or whether it works today. The repo's own data points the other way: 5+ years without a commit, 305 open issues, and the newest issue unanswered.
- **"Used by thousands of podcasters"** (README), UNVERIFIED. No users, numbers or source are given.
- **It turns an audio file into a transcript** (README description), PROBABLE. This is the project's own description. The snapshot gives no accuracy figures, and the engine it wraps is not named. *The verdict rests on this claim.*
- **"Does not run on Apple silicon"** (newest open issue, no reply), UNVERIFIED. It is one user's report with no maintainer response. The context says "Mac mini" but not which chip. *The verdict rests on this claim; the trial is meant to settle it.*

**FIT:**
- **Goal:** goal 3, a transcript with every episode. No transcription tool is in the list of tools in use.
- **Overlap:** none found. Reaper, ffmpeg (used only by loudness.py), Buzzsprout, Mailchimp, Google Docs and Hugo don't transcribe.
- **Burden:** one weekly run per 45-minute episode, plus a manual proofread. It also means keeping an unmaintained tool working on macOS.
- **Cost:** the wrapper is free (MIT, read 2026-10-09). The engine it wraps is not named in the snapshot. If that engine needs a paid API key or an account, the plan becomes needs-decision (money/account), because both need the host's approval.
- **Risks:**
  - **License:** MIT is fine, both as a tool on our machines and on the site.
  - **Platform:** possibly broken on Apple silicon.
  - **Project health:** abandoned in practice. There has been no push since 2021-06-18, and 305 issues are open.
  - **Data:** if the engine is a cloud service, episode audio leaves the machine. That is not listener data, but it is a new party.
  - **Install path:** not shown in the snapshot.

**NEXT ACTION:** The operator installs speechwrap on the Mac mini and transcribes one finished episode. Before installing, they check from its README or source which engine it calls and whether that engine needs a key or account.
- **Done when:** one episode's transcript exists, and the operator has recorded how long it took to proofread.
- **Stop condition:** stop if it does not install or run on the Mac mini, if the engine needs a paid key or new account (that goes back as needs-decision), or if proofreading the transcript takes longer than an hour.
- **Hand-off:** none.

**CONFIDENCE:** medium. The context file is present, and the item is read from a snapshot. It is limited because two claims the verdict rests on are not settled: whether it works at all (PROBABLE) and the Apple silicon report (UNVERIFIED). The wrapped engine is also not named, and the Mac mini's chip is unknown.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/speechwrap@main (no SHA in snapshot; MIT, 12,000 stars, last push 2021-06-18, not archived, 305 open issues; snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "12k stars", "evidence": "meta.json: stars 12000", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "12k stars, so it has to be good", "evidence": "popularity only; repo data shows no commit since 2021-06-18, 305 open issues, newest issue unanswered", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "Used by thousands of podcasters", "evidence": "README assertion, no source or numbers", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "turns an audio file into a transcript", "evidence": "project's own description in snapshot; no accuracy data, engine not named", "status": "PROBABLE"},
    {"claim": "does not run on Apple silicon", "evidence": "newest open issue, one user report, no maintainer reply; Mac mini chip not stated in context", "status": "UNVERIFIED"}
  ],
  "fit": {"goal": "publish a transcript with every episode (goal 3)",
          "overlap": "none found: no transcription tool in use",
          "burden": "one weekly run per 45-minute episode plus proofreading; keeping an unmaintained tool working on macOS",
          "risks": ["unmaintained: no push since 2021-06-18, 305 open issues",
                    "may not run on Apple silicon (unanswered issue)",
                    "wrapped engine not named: may need a paid key/account or send episode audio to a cloud service",
                    "MIT license: acceptable for local tools and site code"],
          "cost": {"price": "free (wrapper)", "tier": "open source", "limits": "engine cost and limits unknown from snapshot",
                   "terms": "MIT", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Check which engine speechwrap calls and whether it needs a key or account, then install it on the Mac mini and transcribe one finished episode",
                  "owner": "operator",
                  "done_when": "one episode transcript exists and the time to proofread it is recorded",
                  "stop_condition": "stop if it does not install or run on the Mac mini, if the engine needs a paid key or new account (return as needs-decision), or if proofreading takes more than an hour",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```