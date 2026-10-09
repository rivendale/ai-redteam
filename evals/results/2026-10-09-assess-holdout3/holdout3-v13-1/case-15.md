VERDICT: skip. None of the fifteen entries says anything about loudness, and goal 4 is already handled by loudness.py, which normalizes every episode to -16 LUFS.

WHAT IT IS: Post "The 15 best podcast microphones of 2026", posted 2026-09-28, at https://posts.example.test/15-best-podcast-microphones-2026. The author is not named in the snapshot. I read a saved copy captured on 2026-10-09 (work/snapshot.md, work/meta.json), not the live page. It is an editors' ranked list: 1. Aria USB, 2. Boomwave XLR, 3. Cardio 7, 4. Dyna Plus, 5. Echo Mini, 6. Fjord SM, 7. Gala One, 8. Halo Voice, 9. Iris Pro, 10. Jade Dynamic, 11. Kite USB, 12. Lark XLR, 13. Moss Mini, 14. Nova Cast, 15. Opal 2. Each entry has two lines on sound quality. No prices are given.

CLAIMS CHECKED:
- **The entries cover sound quality only, with nothing on loudness levelling, gain or normalization.** The post's own text says so. CONFIRMED. The verdict rests on this claim.
- **The list is ranked "best first" by the editors.** The post gives no test method, no measurements and no criteria. UNVERIFIED. The verdict does not rest on it.
- **The sender's question: is one of these microphones useful for goal 4?** Nothing in the post links any microphone to keeping loudness consistent between episodes. A microphone's sound character does not do that job anyway; normalizing the finished episode does.

FIT:
- **Goal:** none found. Goal 4 (consistent loudness) is the one the sender named, and the post has nothing on it.
- **Overlap:** loudness.py already normalizes each finished episode to -16 LUFS with ffmpeg's loudnorm. It also logs the loudness before and after to loudness.log.
- **Burden:** none, since there is nothing to adopt.
- **Cost:** no prices are listed in the post. Any purchase would be hardware against a $0 budget unless approved, and that decision does not arise here.
- **Risks:** none relevant. It is a listicle with an unexplained ranking.

NEXT ACTION: The operator closes this request and keeps goal 4 with loudness.py.
- Done-when: the sender is told the post does not address loudness, and that loudness.log is the place to check consistency.
- Hand-off: none.

CONFIDENCE: high. The item is resolved from a dated snapshot, the claim the verdict rests on is confirmed by the post's own text, and the context file is present. One limit: I read a saved copy, not the live page.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post",
           "identity": "\"The 15 best podcast microphones of 2026\", posted 2026-09-28, author not named; saved snapshot captured 2026-10-09",
           "resolved": true},
  "claims": [
    {"claim": "the entries cover sound quality only; none mentions loudness levelling, gain or normalization",
     "evidence": "the post's own text: each entry is two lines on sound quality, none mentions loudness levelling, gain or normalization",
     "status": "CONFIRMED"},
    {"claim": "the fifteen microphones are ranked best first by the editors",
     "evidence": "no test method, measurements or criteria given",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "none found; goal 4 (consistent loudness) is not addressed by any entry",
          "overlap": "loudness.py already normalizes every episode to -16 LUFS with ffmpeg loudnorm and logs before/after to loudness.log",
          "burden": "none",
          "risks": ["unexplained editorial ranking; no relevant risk since nothing is adopted"],
          "cost": {"price": "not listed in the post", "tier": "n/a", "limits": "n/a", "terms": "n/a",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Close the request and keep goal 4 with loudness.py; point the sender to loudness.log for consistency checks",
                  "owner": "operator",
                  "done_when": "the sender is told the post does not address loudness and that loudness.py already covers goal 4",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```