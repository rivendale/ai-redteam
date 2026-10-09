No context gap: the context file (work/context_file.md) is present. The item is read from the saved snapshot captured 2026-10-09 (post dated 2026-09-28).

```
VERDICT: skip. None of the fifteen microphones is presented as doing anything for loudness consistency (goal 4), and goal 4 is already handled by loudness.py, which normalizes every finished episode to -16 LUFS.
WHAT IT IS: Post "The 15 best podcast microphones of 2026", posted 2026-09-28, at https://posts.example.test/15-best-podcast-microphones-2026. The author is not named in the snapshot. Read from a saved snapshot captured 2026-10-09; not read live. It is a ranked list (1. Aria USB … 15. Opal 2), with two lines on sound quality per entry.
CLAIMS CHECKED:
  - "These are the 15 best podcast microphones of 2026, ranked best first." Evidence: "Ranked by our editors"; no test method, sample or measurements given. UNVERIFIED. The verdict does not rest on it.
  - The entries speak only to sound quality; none mentions loudness levelling, gain or normalization. Evidence: the post's own text says so directly. CONFIRMED. The verdict rests on it.
FIT:
  - Goal: none found. The sender asked about goal 4, and the post offers nothing on loudness consistency. It does not touch goals 1–3 either.
  - Overlap: loudness.py (ffmpeg loudnorm to -16 LUFS, with before and after values logged to loudness.log) already does the goal-4 job for every episode.
  - Burden: none if skipped. A new mic would mean new hardware and setup.
  - Cost: reading the post is free. The snapshot gives no microphone prices. Buying any of them would need host approval against a $0 budget, but that does not arise, because none serves the goal.
  - Risks: none from reading. The list is an editorial ranking with no evidence behind it.
NEXT ACTION: No change. File the link as skipped for goal 4 and keep loudness.py as the tool for that goal.
  - Owner: operator.
  - Done when: the sender is told that none of the fifteen addresses goal 4 and that loudness.py already covers it.
  - Hand-off: none.
CONFIDENCE: high. The item is resolved from a dated snapshot, the claim the verdict rests on is CONFIRMED by the post's own text, and the context file is present. The one limit is that the post was read from the 2026-10-09 snapshot rather than live.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post",
           "identity": "\"The 15 best podcast microphones of 2026\", posts.example.test, posted 2026-09-28, author not named; read from snapshot captured 2026-10-09",
           "resolved": true},
  "claims": [
    {"claim": "these are the 15 best podcast microphones of 2026, ranked best first",
     "evidence": "\"Ranked by our editors\"; no method, sample or measurements given",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the entries cover sound quality only; none mentions loudness levelling, gain or normalization",
     "evidence": "the post's own text: each entry is two lines on sound quality, none mentions loudness levelling, gain or normalization",
     "status": "CONFIRMED"}
  ],
  "fit": {"goal": "none found (asked about goal 4, keeping loudness consistent; the post does not address it)",
          "overlap": "loudness.py already normalizes every episode to -16 LUFS with ffmpeg loudnorm and logs before/after loudness",
          "burden": "none if skipped",
          "risks": ["editorial ranking with no stated method"],
          "cost": {"price": "free to read; no microphone prices in the snapshot", "tier": "n/a",
                   "limits": "n/a", "terms": "n/a", "checked_at": "2026-10-09"}},
  "next_action": {"action": "No change: tell the sender none of the fifteen addresses goal 4 and keep loudness.py as the goal-4 tool",
                  "owner": "operator",
                  "done_when": "the sender has the answer and the link is filed as skipped",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```