VERDICT: skip. The post's own table refutes its headline: 3 of its 10 episodes missed -16 LUFS by more than 1 LU. It also does the same job loudness.py already does, so it gives no reason to think it would steady goal 4.

WHAT IT IS: A post titled "LevelRight hits -16 LUFS on every episode", posted 2026-09-18, at https://posts.example.test/leveler-hits-minus-16. I read the saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not the live page. The snapshot names no author. It also gives no price, license, platform or description of how LevelRight works.

CLAIMS CHECKED:
- **"It hits the target on every episode" (-16.0 LUFS): REFUTED. Load-bearing.**
  - Episodes 1, 2, 3, 5, 7, 8 and 10 landed within 0.2 LU of -16.
  - Episode 4 measured -17.9, episode 6 measured -14.8 and episode 9 measured -17.4.
  - The spread is 3.1 LU across ten episodes. Common delivery targets allow about ±1 LU, and three episodes are outside that.
- **"We ran it on ten episodes and measured with ffmpeg": PROBABLE. Not load-bearing.**
  - The table is consistent with this, but the post doesn't name the ffmpeg filter or say whether the reading is integrated loudness.
  - The sample is ten episodes of unknown source material.
  - Nothing compares LevelRight with another tool, including ffmpeg loudnorm.
- **"Is it better than loudness.py?" (your question): the post doesn't answer it.** It has no head-to-head comparison. On its own numbers it misses target in 30% of episodes, which is not a result that beats a working normalizer.

FIT:
- **Goal:** It is aimed at goal 4 (consistent loudness between episodes).
- **Overlap:** loudness.py already normalizes every episode to -16 LUFS with ffmpeg loudnorm and logs the before and after values to loudness.log. LevelRight would do the same job.
- **Burden:** It would add a tool, and probably an account, alongside or in place of loudness.py.
- **Cost:** Not stated in the post (checked 2026-10-09). Any paid tier or account would need the host's approval, and the quarter's budget is $0.
- **Risks:** The license is unknown. Whether it runs on a Mac is unknown. Whether audio leaves the machine is unknown.

So the wobble in goal 4 is better investigated in our own pipeline than fixed with this tool. One thing worth checking: single-pass loudnorm runs in dynamic mode and can land off target. Two-pass loudnorm, which measures first and then applies linear gain, usually hits target more tightly. This is a hypothesis to test against our own numbers, not a finding.

NEXT ACTION: The operator reads the "after" values in loudness.log for the last 10 episodes. This shows whether the wobble is in our normalization or somewhere after it, such as perceived loudness or what Buzzsprout serves.
- **Owner:** operator.
- **Done when:** the after-values are listed with their spread and compared to the post's 3.1 LU spread.
- **Hand-off:** none.

CONFIDENCE: High. I read the item from a saved snapshot. The claim the verdict rests on is refuted by the post's own table, and the context file is present. Price, license and method are absent from the post, but the verdict doesn't depend on them.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post",
           "identity": "post 'LevelRight hits -16 LUFS on every episode', posted 2026-09-18, author not named, https://posts.example.test/leveler-hits-minus-16 (saved snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "LevelRight hits -16 LUFS on every episode",
     "evidence": "the post's own table: episodes 4 (-17.9), 6 (-14.8) and 9 (-17.4) miss by more than 1 LU; spread 3.1 LU over ten episodes",
     "status": "REFUTED"},
    {"claim": "it was run on ten episodes and measured with ffmpeg",
     "evidence": "table of ten results; ffmpeg filter and measurement mode not named; no comparison with another tool",
     "status": "PROBABLE", "load_bearing": false}
  ],
  "fit": {"goal": "consistent loudness between episodes (goal 4)",
          "overlap": "loudness.py already normalizes every episode to -16 LUFS with ffmpeg loudnorm and logs before/after to loudness.log",
          "burden": "a new tool, and possibly an account, alongside or replacing loudness.py",
          "risks": ["license not stated", "Mac support not stated", "whether audio leaves the machine not stated"],
          "cost": {"price": "not stated in the post", "tier": "not stated", "limits": "not stated",
                   "terms": "not stated", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Read the after-values for the last 10 episodes in loudness.log to find whether the goal-4 wobble is in our normalization or after it (e.g. try two-pass loudnorm if after-values spread)",
                  "owner": "operator",
                  "done_when": "the last 10 after-values are listed with their spread and compared with the post's 3.1 LU spread",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```