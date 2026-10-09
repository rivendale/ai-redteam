**VERDICT:** skip. LevelRight does the same job as loudness.py, and the post's own table shows it misses -16 LUFS on 3 of 10 episodes, so it gives no evidence it would steady goal 4.

**WHAT IT IS:** A post titled "LevelRight hits -16 LUFS on every episode", posted 2026-09-18. The author is not named in the snapshot. I read it from a saved copy captured 2026-10-09 (work/snapshot.md, work/meta.json), not live. The post does not give LevelRight's price, license, platform or install path.

**CLAIMS CHECKED:**
- **"It hits the target on every episode" (-16.0 LUFS): REFUTED. The verdict rests on this.** The post's own table contradicts it:
  - Episode 4 measured -17.9 (1.9 LU low).
  - Episode 6 measured -14.8 (1.2 LU high).
  - Episode 9 measured -17.4 (1.4 LU low).
  - The other seven fall within ±0.2 LU. The full spread is 3.1 LU.
- **"Ran on ten episodes, measured with ffmpeg": UNVERIFIED.** The post says this but gives no further detail:
  - It does not say whose episodes these were, or how long or varied they were.
  - It does not say which ffmpeg measurement was used (integrated loudness, ebur128 or loudnorm's print).
- **The sender's question, "is it better than loudness.py?": UNVERIFIED. The verdict rests on this.** Nothing in the post compares LevelRight with ffmpeg loudnorm or any other tool. Its own results include misses larger than a normalizer is usually expected to make.

**FIT:**
- **Goal:** Goal 4, keeping loudness consistent from one episode to the next.
- **Overlap:** Full overlap. loudness.py already normalizes every finished episode to -16 LUFS with ffmpeg loudnorm, and it logs the before and after values to loudness.log.
- **Burden:** A second normalizer in the chain, plus whatever install and account it needs. The post does not say.
- **Cost:** Unknown. The post gives no price, tier or terms. Constraints apply: no new paid subscription or account without the host's approval, and a $0 tool budget this quarter.
- **Risks:**
  - License unknown.
  - Mac support unknown.
  - Install path unknown.
  - It is unclear whether audio leaves the machine.

**NEXT ACTION:**
- **Action:** Find where the goal 4 wobble comes from before looking for a replacement. Read the "after" values in loudness.log for the last 10 or more episodes.
  - If the after values sit near -16, the wobble is not integrated loudness. It is more likely perceived level, such as dynamics, true-peak limiting or a segment mix.
  - If the after values vary, check whether loudness.py runs loudnorm in a single pass. Linear two-pass mode is the usual fix.
- **Owner:** Operator.
- **Done when:** The log's after values are listed, and the wobble is traced to a cause, or loudness.py is shown not to be the cause.
- **Hand-off:** None.

**CONFIDENCE:** Medium. It is limited by three things:
- I read a saved snapshot, not the live post.
- No comparison with loudness.py exists, so "better" is UNVERIFIED.
- LevelRight's cost and terms are not stated.

The refutation itself is solid, because it comes from the post's own data.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post", "identity": "post 'LevelRight hits -16 LUFS on every episode', posted 2026-09-18, author not named; saved snapshot captured 2026-10-09",
           "resolved": true},
  "claims": [
    {"claim": "LevelRight hits -16 LUFS on every episode", "evidence": "the post's own table: episode 4 at -17.9, episode 6 at -14.8, episode 9 at -17.4 LUFS; spread 3.1 LU", "status": "REFUTED"},
    {"claim": "tested on ten episodes and measured with ffmpeg", "evidence": "stated in the post; no source episodes or ffmpeg method given", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "it is better than our loudness.py (sender's question)", "evidence": "the post makes no comparison with ffmpeg loudnorm or any other tool", "status": "UNVERIFIED"}
  ],
  "fit": {"goal": "goal 4: keep loudness consistent from one episode to the next",
          "overlap": "loudness.py already normalizes every episode to -16 LUFS with ffmpeg loudnorm and logs before/after values",
          "burden": "a second normalizer step; install and account needs not stated",
          "risks": ["license not stated", "Mac support and install path not stated", "unknown whether audio leaves the machine"],
          "cost": {"price": "not stated in the post", "tier": "not stated", "limits": "not stated", "terms": "not stated",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Read the after values in loudness.log for the last 10+ episodes to find whether the goal 4 wobble is integrated loudness (check loudnorm single vs two-pass) or perceived level",
                  "owner": "operator", "done_when": "the after values are listed and the wobble is traced to a cause, or loudness.py is shown not to be it",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```