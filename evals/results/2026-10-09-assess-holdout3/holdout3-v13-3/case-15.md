```
VERDICT: skip. None of the fifteen microphones does anything for goal 4: the post ranks sound quality only, and loudness consistency is already handled after recording by loudness.py (every episode normalized to -16 LUFS).
WHAT IT IS: Post "The 15 best podcast microphones of 2026", posted 2026-09-28, author not named in the
  capture. Read from a saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not live. It is an
  editors' ranked list (1. Aria USB through 15. Opal 2), with two lines on sound quality per entry. No prices, specs
  or test method are given.
CLAIMS CHECKED:
  - "None of the 15 entries addresses loudness levelling, gain or normalization." Evidence: the snapshot's own text
    says so, and the entries are about sound quality only. CONFIRMED. The verdict rests on this.
  - "These are the 15 best podcast microphones of 2026, best first." Evidence: "Ranked by our editors", with no
    method, no measurements and no sample. UNVERIFIED. The verdict does not rest on it.
  - The sender's implied premise that a microphone could serve goal 4. Nothing in the post supports it. Loudness
    consistency between episodes is set at the mastering step, not by the mic. UNVERIFIED as far as the item goes.
    The verdict does not rest on it.
FIT:
  - Goal: none found. The post offers nothing for goal 4 (consistent loudness), and nothing for goals 1–3 either.
  - Overlap: loudness.py already does this job. It normalizes each finished episode to -16 LUFS with ffmpeg loudnorm
    and logs loudness before and after to loudness.log.
  - Burden: none, since nothing is adopted. Buying a mic would mean a purchase and changing the recording setup.
  - Cost: the post gives no prices (as read 2026-10-09). Any purchase would need approval against the $0 quarterly
    budget, but the item serves no goal, so that trade-off never comes up.
  - Risks: none to us from reading it. The post is a listicle with an unexplained ranking.
NEXT ACTION: Close the link as skip. If loudness still seems inconsistent between episodes, check loudness.log
  first: the "after" values should all sit at about -16 LUFS. Owner: operator. Done when the link is filed as skip.
  Hand-off: none.
CONFIDENCE: high. The item was read in full from the 2026-10-09 snapshot, the claim the verdict rests on is
  CONFIRMED from the item's own text, and the context file is present. The only limit is that this was a saved
  copy, not a live read.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post",
           "identity": "\"The 15 best podcast microphones of 2026\", posts.example.test, posted 2026-09-28, author not named; read from snapshot captured 2026-10-09",
           "resolved": true},
  "claims": [
    {"claim": "none of the 15 entries addresses loudness levelling, gain or normalization",
     "evidence": "the snapshot text: each entry is two lines on sound quality, none mentions loudness, gain or normalization",
     "status": "CONFIRMED"},
    {"claim": "these are the 15 best podcast microphones of 2026, ranked best first",
     "evidence": "'Ranked by our editors', no method, measurements or sample given",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "a microphone from this list could help keep loudness consistent between episodes (sender's premise)",
     "evidence": "nothing in the post addresses it; loudness consistency is set at mastering, which loudness.py already does",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (goal 4, consistent loudness, is not addressed by the post)",
          "overlap": "loudness.py already normalizes every episode to -16 LUFS with ffmpeg loudnorm and logs before/after to loudness.log",
          "burden": "none if skipped; a mic purchase would change the recording setup",
          "risks": ["unexplained editorial ranking, no test method"],
          "cost": {"price": "not given in the post", "tier": "n/a", "limits": "n/a",
                   "terms": "n/a; any purchase would need approval against the $0 quarterly budget",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Close the link as skip; if loudness still seems inconsistent, check that the 'after' values in loudness.log sit at about -16 LUFS",
                  "owner": "operator",
                  "done_when": "the link is filed as skip",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```