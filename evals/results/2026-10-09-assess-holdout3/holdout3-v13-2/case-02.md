VERDICT: skip. The post's own table shows LevelRight missing -16 LUFS on 3 of 10 episodes, and loudness.py already does the same job, so nothing here shows it is better than what we run.

WHAT IT IS: Post "LevelRight hits -16 LUFS on every episode", posted 2026-09-18. The snapshot names no author. I read the saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not the live page. The post gives no price, license, platform or install path for LevelRight, and no description of how it works.

CLAIMS CHECKED:
- **"It hits the target on every episode" (-16.0 LUFS).** Load-bearing. **REFUTED** by the post's own table:
  - Seven episodes land within 0.2 LU of -16.0.
  - Episode 4 reads -17.9 (1.9 LU low), episode 6 reads -14.8 (1.2 LU high) and episode 9 reads -17.4 (1.4 LU low).
  - A 1-2 LU swing between episodes is the kind of wobble goal 4 is about.
- **"Ran on ten episodes, measured with ffmpeg."** Not load-bearing. **UNVERIFIED.** The post gives no ffmpeg command or filter settings, and it does not say whose episodes these were or what their source loudness was. With ten samples and no stated method, this is the authors' own report, not a test we can repeat.
- **The sender's implied claim, "it is better than loudness.py."** Not load-bearing. **UNVERIFIED.** The post never compares LevelRight with ffmpeg loudnorm or any other tool. Nothing in it shows LevelRight beating our script, and its own spread looks no tighter than what we would expect from loudnorm.

FIT:
- **Goal:** It targets goal 4 (consistent loudness between episodes).
- **Overlap:** loudness.py already normalizes every episode to -16 LUFS with ffmpeg loudnorm and logs the before and after values. LevelRight would do the same job.
- **Burden:** It would be a new tool in the chain on a Mac, with an install path the post doesn't describe.
- **Cost:** The post states no price or terms. The constraints set a $0 budget and require approval for any new paid account.
- **Risks:** License and telemetry are unknown. Our audio files would go to a new tool, and if it is a hosted service, to a new party.
- **The useful lead:** The question is why goal 4 still wobbles with loudness.py. Our own loudness.log can answer it, because it already records the after-values. One possibility I cannot check without seeing loudness.py: loudnorm run in a single pass works in dynamic mode and can miss the target. Two-pass loudnorm in linear mode usually lands closer. Treat this as a hypothesis to check, not a finding.

NEXT ACTION: Read the "after" values in loudness.log for the last 10 or more episodes.
- **Owner:** operator, or whoever maintains loudness.py.
- **Done when:** We know whether the finished episodes are actually off -16 LUFS:
  - If they are off, check how loudness.py calls loudnorm (single-pass or two-pass/linear).
  - If they are on target, the wobble is elsewhere, for example in perceived loudness, true-peak limiting, or a step after loudness.py.
- **Hand-off:** none.

CONFIDENCE: high. The item is resolved from a dated snapshot, the claim the verdict rests on is refuted by the post's own data, and the context file is present. The one limit is that I worked from the snapshot, not the live page.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post",
           "identity": "post 'LevelRight hits -16 LUFS on every episode', posted 2026-09-18, author not given; read from snapshot captured 2026-10-09",
           "resolved": true},
  "claims": [
    {"claim": "LevelRight hits -16 LUFS on every episode",
     "evidence": "the post's own table: episode 4 -17.9, episode 6 -14.8, episode 9 -17.4 LUFS; 7 of 10 within 0.2 LU",
     "status": "REFUTED"},
    {"claim": "ran on ten episodes and measured the result with ffmpeg",
     "evidence": "stated in the post; no command, settings, episode source or input loudness given",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "LevelRight is better than our loudness.py (sender's question)",
     "evidence": "the post makes no comparison with ffmpeg loudnorm or any other tool",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "keep loudness consistent from one episode to the next (goal 4)",
          "overlap": "loudness.py already normalizes every episode to -16 LUFS with ffmpeg loudnorm and logs before/after",
          "burden": "a new tool in the chain, install path not described",
          "risks": ["license not stated", "telemetry and data handling not stated", "possible new party receiving our audio if hosted"],
          "cost": {"price": "not stated in the post", "tier": "not stated", "limits": "not stated",
                   "terms": "not stated", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Read the after-values in loudness.log for the last 10+ episodes to see whether finished episodes are off -16 LUFS; if they are, check whether loudness.py runs loudnorm single-pass or two-pass/linear",
                  "owner": "operator",
                  "done_when": "we know whether the wobble is in loudness.py's output or somewhere else in the chain",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```