VERDICT: watch. The sender's "98% accurate on any audio" is refuted by the post itself: 98% was on studio audio only, noisy recordings scored 78%, and the post never names the transcriber, so there is nothing to adopt yet.

WHAT IT IS: Post "We tested a transcriber," dated 2026-10-01. The author is not given. Read from a saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json); the live page was not opened. The post names no product, price, tier or terms.

CLAIMS CHECKED:
- **"98% accurate on any audio"** (research agent's summary). **REFUTED**, and the verdict rests on it. The post gives 98% only for the 3 studio-quality episodes. The 3 noisy field recordings scored 78%, and the overall figure is 88%.
- **98% word accuracy on studio audio.** **PROBABLE**, not load-bearing. It rests on 3 episodes, one native-English speaker each, with no method given: no metric definition, no reference transcript source, no audio length. Two things would change it: a test with several speakers (guests, crosstalk) or accented speech, or a stated method.
- **78% on noisy field recordings.** **PROBABLE**, not load-bearing. Same design and limits as above.
- **88% overall.** **CONFIRMED**, not load-bearing. It is consistent with the two halves: (3×98 + 3×78) / 6 = 88.
- **"Strong result, so we should use it"** (summary's inference). **UNVERIFIED**, not load-bearing. The post makes no recommendation, does not identify a tool we could use, and tests only single-speaker audio. Whether it fits our episodes is not settled by the post.

FIT:
- **Goal:** a transcriber would serve goal 3, "publish a transcript with every episode."
- **Overlap:** nothing in use transcribes today.
- **Burden:** unknown, because the tool is unnamed.
- **Cost:** unknown, because no product, price or terms appear in the post (checked 2026-10-09).
- **Risks:** a hosted transcriber would likely mean a new account, possibly a paid one, and sending episode audio to a new party. Each of those needs the host's approval under our constraints. At 78% on noisy audio, the transcripts would need heavy hand-correction. That works against goal 1 (editing time under 2 hours per episode).

NEXT ACTION: The operator asks the research agent to name the transcriber the post tested, and to send its product page for a fresh `assess`.
- **Owner:** operator.
- **Done when:** the tool's name and its product page link are in hand.
- **Stop condition:** none (not a try).
- **Hand-off:** none.

CONFIDENCE: high. The item is resolved from a dated snapshot, the context file is present, and the one claim the verdict rests on is refuted by the post's own numbers. Two gaps remain: the tool is unnamed, and we do not know how our own audio compares to the test conditions. Neither would turn this into adopt.

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "post",
           "identity": "post 'We tested a transcriber', posted 2026-10-01, author not given, read from snapshot captured 2026-10-09; names no product, price or terms",
           "resolved": true},
  "claims": [
    {"claim": "the transcriber is 98% accurate on any audio (research agent's summary)",
     "evidence": "the post: 98% on 3 studio episodes, 78% on 3 noisy field recordings, 88% overall",
     "status": "REFUTED"},
    {"claim": "98% word accuracy on studio-quality audio",
     "evidence": "3 episodes, one native-English speaker each, no method or metric definition given",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "78% word accuracy on noisy field recordings",
     "evidence": "3 episodes, one native-English speaker each, no method given",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "88% overall across six episodes",
     "evidence": "consistent with the two halves: (3x98 + 3x78) / 6 = 88",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "a strong result, so we should use it (research agent's inference)",
     "evidence": "the post makes no recommendation, names no tool, and tests only single-speaker audio",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "publish a transcript with every episode (goal 3)",
          "overlap": "nothing in use transcribes today",
          "burden": "unknown: the tool is not named",
          "risks": ["a hosted transcriber likely needs a new account and sends episode audio to a new party (host approval required)",
                    "78% on noisy audio means heavy hand-correction, against goal 1 (editing under 2 hours)",
                    "tested only one native-English speaker per episode; guests and crosstalk untested"],
          "cost": {"price": "unknown: no product named", "tier": "unknown", "limits": "unknown",
                   "terms": "unknown", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Ask the research agent to name the transcriber the post tested and send its product page for a fresh assess",
                  "owner": "operator",
                  "done_when": "the tool's name and its product page link are in hand",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```