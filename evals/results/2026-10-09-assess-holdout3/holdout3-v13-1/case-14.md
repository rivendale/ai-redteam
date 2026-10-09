VERDICT: skip. The talk argues for going video, but "the show stays audio only" is already decided, and the talk's own numbers (editing up from 4 to 11 hours per episode) run against goal 1, keeping editing under 2 hours.

WHAT IT IS: A conference talk, "Why every podcast should be a video podcast" (transcript, 36 minutes), at https://talks.example.test/why-video-podcasts. It was posted 2026-09-16, and the speaker is not named in the snapshot. I read it from a saved snapshot captured on 2026-10-09 (work/snapshot.md, work/meta.json), not live. The snapshot is two sentences, far shorter than a 36-minute transcript, so it may be an excerpt rather than the full text.

CLAIMS CHECKED:
- **"Video drives discovery" / "If you are audio only you are invisible."**
  - Evidence: none in the snapshot. It is the speaker's assertion, with no data on reach, downloads or discovery sources.
  - Status: UNVERIFIED. Nothing in the item settles it either way.
  - The verdict does not rest on it.
- **The speaker's studio added a camera operator and a video editor, and now spends about 11 hours editing per episode, up from 4.**
  - Evidence: the speaker's own account of one studio.
  - Status: PROBABLE as a report of that studio's experience. It is a single case with no method given.
  - The verdict rests on it: video nearly tripled editing time in the talk's own example.
- **Inference: the extra editing was worth it.**
  - The snapshot reports no outcome from going video, such as more downloads, listeners or signups.
  - Status: UNVERIFIED.
  - The verdict does not rest on it.

FIT:
- **Goal:** None found.
  - It works against goal 1 (cut editing time to under 2 hours). The talk's own example shows editing rising from 4 to 11 hours.
  - It does not address goal 2 (newsletter signups), goal 3 (transcripts) or goal 4 (loudness). "Discovery" is not the newsletter goal.
- **Overlap:** It conflicts with what is already decided ("The show stays audio only") rather than overlapping with a tool.
- **Burden:** Following the talk means a camera operator, a video editor or video editing work, and a video workflow alongside Reaper. The talk's example adds about 7 editing hours per episode on a weekly show.
- **Cost:** Reading or watching the talk costs nothing as captured. Acting on it would mean new staff or equipment against a $0 budget. No prices are given in the item. Checked 2026-10-09 from the snapshot.
- **Risks:** It would reopen a settled decision and push editing time further from goal 1. There are no license or data risks, because nothing is installed.

NEXT ACTION: The operator replies to the sender: "Skip. We decided the show stays audio only, and the talk's own example shows editing going from 4 to 11 hours per episode, against our under-2-hours goal." Done when the reply is sent. Hand-off: none. If the host ever wants to reopen the audio-only decision, that is a separate decision for the host, not an outcome of this assessment.

CONFIDENCE: medium. The context file is present, and the claim the verdict rests on is PROBABLE. Confidence is held back from high because the item was read only from a saved snapshot that looks like an excerpt of a 36-minute talk, and the full transcript was not available. The fuller text is unlikely to change the verdict, which rests mainly on the standing audio-only decision.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post",
           "identity": "talk 'Why every podcast should be a video podcast' (transcript, 36 min), https://talks.example.test/why-video-podcasts, posted 2026-09-16, speaker not named; read from saved snapshot captured 2026-10-09",
           "resolved": true},
  "claims": [
    {"claim": "video drives discovery; audio-only podcasts are invisible",
     "evidence": "speaker's assertion only; no data on reach or discovery in the snapshot",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the speaker's studio added a camera operator and video editor and now edits about 11 hours per episode, up from 4",
     "evidence": "speaker's own account of one studio, no method given",
     "status": "PROBABLE"},
    {"claim": "the added editing time paid off for the studio",
     "evidence": "no outcome (downloads, listeners, signups) reported in the snapshot",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "none found; works against goal 1 (editing under 2 hours per episode)",
          "overlap": "conflicts with the decision that the show stays audio only",
          "burden": "camera operator, video editor or video editing work, and a video workflow beside Reaper; about 7 more editing hours per episode in the talk's example",
          "risks": ["reopens a settled decision (audio only)", "moves editing time further from goal 1"],
          "cost": {"price": "talk is free to read as captured; going video needs staff or equipment, unpriced in the item",
                   "tier": "n/a", "limits": "none stated",
                   "terms": "none stated", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Reply to the sender: skip, because the show stays audio only and the talk's own example shows editing going from 4 to 11 hours per episode, against our under-2-hours goal",
                  "owner": "operator", "done_when": "reply sent to the sender",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```