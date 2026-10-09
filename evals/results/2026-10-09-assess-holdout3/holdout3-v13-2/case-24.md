```
VERDICT: watch. The forwarded summary misstates the post: the post reports 98% only on studio audio and 78% on noisy audio, and it never names the transcriber, its price or its terms, so there is nothing to adopt yet.
WHAT IT IS: Post "We tested a transcriber", dated 2026-10-01, author not given, at https://posts.example.test/transcriber-accuracy-test. Read from a saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not live. The post does not name the transcriber.
CLAIMS CHECKED:
  - "98% accurate on any audio" (the research agent's summary) — REFUTED. The post's own table gives 78% on noisy field recordings and 88% overall. 98% is the studio-only figure. [verdict rests on this]
  - 98% word accuracy on studio-quality audio — PROBABLE, but narrow. Evidence is the post's own test: 3 episodes, one speaker each, native English. It does not say how word accuracy was measured (no WER method, no reference transcripts described). Two hosts, guests, crosstalk or accents were not tested. Any of those could change the result.
  - 78% on noisy field recordings — PROBABLE. Same design and the same limits, 3 episodes.
  - 88% overall — CONFIRMED as arithmetic. It is the mean of 98 and 78 over 3+3 episodes.
  - "strong result, recommend we use it" (the sender's inference) — not supported. A 6-episode, single-speaker test of an unnamed tool does not support a recommendation to use it.
FIT:
  - Goal: Goal 3 (publish a transcript with every episode) would be served by some transcriber.
  - Overlap: nothing in use transcribes today.
  - Burden: unknown, because the tool is unnamed. Expect at least one step per episode, and likely a new account.
  - Cost: not stated in the post (checked 2026-10-09). Any paid plan or account needs the host's approval, and the budget is $0.
  - Risks: tool identity, license, install path and data handling are all unknown. Episode audio may leave the machine. The test is too small to say how it does on our episodes.
NEXT ACTION: The operator asks the research agent which transcriber the post tested and for a link to its current pricing and terms page, then re-runs assess on that product page. Done when the tool's name and pricing/terms link are in hand. Hand-off: none.
CONFIDENCE: high. The post is resolved from a saved copy, and the claim the verdict rests on is refuted by the post's own numbers. Limits: no author is named, and nothing about the tool itself can be judged until it is identified.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "post",
           "identity": "\"We tested a transcriber\", posted 2026-10-01, author not given, https://posts.example.test/transcriber-accuracy-test (saved snapshot captured 2026-10-09); transcriber not named",
           "resolved": true},
  "claims": [
    {"claim": "the transcriber is 98% accurate on any audio (research agent's summary)",
     "evidence": "post's own figures: 78% on noisy field recordings, 88% overall; 98% is studio-only",
     "status": "REFUTED"},
    {"claim": "98% word accuracy on studio-quality audio",
     "evidence": "post's own test of 3 episodes, one native-English speaker each, measurement method not given",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "78% word accuracy on noisy field recordings",
     "evidence": "post's own test of 3 episodes, same design",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "88% overall accuracy across six episodes",
     "evidence": "mean of 98% and 78% over two groups of 3 episodes",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "this is a strong result that justifies using the tool (sender's inference)",
     "evidence": "6 single-speaker episodes, unnamed tool, no method; does not support a use recommendation",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "publish a transcript with every episode (goal 3)",
          "overlap": "none: nothing in use transcribes",
          "burden": "unknown until the tool is named; likely a per-episode step and an account",
          "risks": ["transcriber not named: license, install path and data handling unknown",
                    "episode audio may leave the machine",
                    "test covers 6 single-speaker native-English episodes only"],
          "cost": {"price": "not stated in the post", "tier": "unknown", "limits": "unknown",
                   "terms": "unknown", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Ask the research agent which transcriber the post tested and for a link to its current pricing and terms page, then assess that product page",
                  "owner": "operator",
                  "done_when": "the tool's name and pricing/terms link are in hand",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```