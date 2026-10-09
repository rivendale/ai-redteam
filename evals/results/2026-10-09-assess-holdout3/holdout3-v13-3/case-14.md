VERDICT: skip. The show is already decided to stay audio only, and the talk's own numbers show that going to video raised editing from 4 to 11 hours per episode. Goal 1 is to get editing under 2 hours, so the talk points the wrong way on our main goal and argues for a change we have already ruled out.

WHAT IT IS: A conference talk transcript, "Why every podcast should be a video podcast" (36 minutes). It was posted 2026-09-16 at https://talks.example.test/why-video-podcasts. I worked from a saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not a live read. The snapshot does not name the speaker. It is also very short for a 36-minute talk (two sentences), so it is probably an excerpt. The verdict does not depend on the parts that are missing.

CLAIMS CHECKED:
- **"Video drives discovery" / "If you are audio only you are invisible."** The snapshot offers no evidence: no data, no comparison, no audience numbers. It is a confident assertion. **UNVERIFIED.** It is not load-bearing.
- **The speaker's studio went from about 4 to about 11 hours of editing per episode after adding video.** This is the speaker's own report about their own studio. It is a single case with no method given, but it is a cost the speaker admits against their own argument. **PROBABLE.** This claim is load-bearing.
- **The sender's description, "a talk about why podcasts should be on video."** It matches the title and the text. **CONFIRMED.** It is not load-bearing.

FIT:
- **Goal:** none found. The talk is about discovery and growing an audience. Our growth goal (goal 2) is newsletter signups, and the talk does not address it. It works against goal 1, since editing time nearly tripled in the speaker's own case.
- **Overlap:** it argues for a choice that is already decided. "The show stays audio only."
- **Burden:** following it would add a camera operator, a video editor, and about 7 more hours of editing per episode, per the talk's own figures. It would also likely mean video hosting beyond Buzzsprout.
- **Cost:** the talk is free to read. Acting on it would need staff and tools, against a $0 budget this quarter.
- **Risks:** none from reading it. Acting on it would break a standing decision.

NEXT ACTION: No action. The operator files this link as skipped. Done when it is recorded as "skip: show stays audio only; talk's own data shows video raises editing time". Hand-off: none.

CONFIDENCE: high. The item is resolved from a dated snapshot, the claim the verdict rests on is PROBABLE, and a context file is present. The only limit is that the snapshot looks like an excerpt of the talk. Even so, nothing in a fuller transcript would change a verdict that rests on the already-decided audio-only rule.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post",
           "identity": "talk transcript 'Why every podcast should be a video podcast' (36 min), posted 2026-09-16, https://talks.example.test/why-video-podcasts, speaker not named; read from snapshot captured 2026-10-09 (appears to be an excerpt)",
           "resolved": true},
  "claims": [
    {"claim": "video drives discovery; audio-only podcasts are invisible", "evidence": "speaker's assertion only, no data in the snapshot", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "adding video took the speaker's studio from about 4 to about 11 hours of editing per episode", "evidence": "speaker's own report in the transcript, single studio, no method", "status": "PROBABLE"},
    {"claim": "the item is a talk about why podcasts should be on video (sender's words)", "evidence": "title and text of the snapshot", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found; it works against goal 1 (editing under 2 hours per episode)",
          "overlap": "already decided: the show stays audio only",
          "burden": "acting on it would add a camera operator, a video editor and about 7 more editing hours per episode (per the talk)",
          "risks": ["acting on it would reverse a standing decision (audio only)", "no risk in reading it"],
          "cost": {"price": "free to read", "tier": "n/a", "limits": "none", "terms": "public talk", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Record the link as skipped: show stays audio only, and the talk's own data shows video raises editing time",
                  "owner": "operator", "done_when": "the link is filed with the skip reason", "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```