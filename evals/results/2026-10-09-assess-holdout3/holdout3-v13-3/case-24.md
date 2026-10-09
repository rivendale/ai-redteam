```
VERDICT: watch. The post refutes the summary's own claim: it reports 98% only on studio audio, 78% on noisy audio and 88% overall, and it never names the transcriber. There is nothing yet to adopt, even though a transcriber would serve goal 3.

WHAT IT IS: Post "We tested a transcriber", posted 2026-10-01, author not given in the snapshot.
  https://posts.example.test/transcriber-accuracy-test, read from a saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json).
  The full post is two lines of results. It does not name the transcriber, its price or its terms.

CLAIMS CHECKED:
  1. Summary: "98% accurate on any audio". REFUTED by the post's own numbers.
     - Noisy field recordings: 78%. Overall: 88%.
     - 98% holds only for the 3 studio-quality episodes.
     - [verdict rests on this]
  2. Post: 98% word accuracy on studio-quality audio. PROBABLE.
     - The post reports it, but the sample is 3 episodes.
     - Every episode had one speaker, a native English speaker.
     - No method is given: how word accuracy was scored, what the reference transcript was, or the episode lengths.
     - What would change it: more episodes, several speakers, accents, crosstalk.
  3. Summary: "strong result". UNVERIFIED as stated, and overstated.
     - The design is 6 episodes, single speaker, native English, no method.
     - That is a small informal test, not a strong result.
     - It cannot be transferred to a show whose speaker count the context file does not record.
  4. Which transcriber was tested. Not stated anywhere in the post (CONFIRMED absent).
     - "Use it" has no referent we can check.
     - [verdict rests on this]

FIT:
  - Goal: goal 3, publish a transcript with every episode. Nothing in use produces transcripts today.
  - Overlap: none found among Reaper, ffmpeg, Buzzsprout, Mailchimp, Google Docs, Hugo and loudness.py.
    Buzzsprout's own transcript features are not mentioned in the context file and were not checked.
  - Burden: unknown until the tool is named. Likely one step per episode, plus correcting the transcript.
    Correction work rises sharply on noisy audio, where the post itself shows 78%.
  - Cost: unknown. No product, price, tier or terms appear in the post (checked 2026-10-09 from the snapshot).
    Any paid plan or new account needs the host's approval, and the budget is $0.
  - Risks:
    - If it is a hosted service, episode audio would leave the machine.
    - Its license and install path are unknown.
    - Accuracy on any field-recorded segments is about 78%.

NEXT ACTION:
  - Action: ask the research agent which transcriber the post tested. If it is named, send that product
    (its page, price and terms) for its own assess.
  - Owner: research agent, reporting to the operator.
  - Done when: the transcriber's name and its product page are in hand, or it is confirmed that the post never names it.
  - Hand-off: none.

CONFIDENCE: high.
  - Both claims the verdict rests on are settled by the post's own text: the "any audio" claim is refuted
    and the tool is unnamed.
  - The context file is present.
  - Limit: this is a saved snapshot from 2026-10-09, not a live read.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "post", "identity": "\"We tested a transcriber\", posted 2026-10-01, author not given; https://posts.example.test/transcriber-accuracy-test (snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "the transcriber is 98% accurate on any audio (research agent's summary)", "evidence": "post's own numbers: 98% studio, 78% noisy field recordings, 88% overall", "status": "REFUTED"},
    {"claim": "98% word accuracy on studio-quality audio", "evidence": "post reports it for 3 episodes, one native-English speaker each, no scoring method given", "status": "PROBABLE",
     "load_bearing": false},
    {"claim": "this is a strong result (research agent's summary)", "evidence": "6 episodes, single speaker, native English, no method; small informal test", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "the post identifies a transcriber we could use", "evidence": "the full post text names no product, price or terms", "status": "REFUTED"}
  ],
  "fit": {"goal": "publish a transcript with every episode (goal 3)", "overlap": "none found in tools in use",
          "burden": "unknown until the tool is named; per-episode transcription plus correction, heavier on noisy audio",
          "risks": ["tool unnamed: license, install path and data handling unknown", "a hosted service would send episode audio off the machine", "about 78% accuracy on noisy field recordings per the post"],
          "cost": {"price": "unknown (product not named)", "tier": "unknown", "limits": "unknown", "terms": "unknown",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Ask the research agent which transcriber the post tested; if named, send that product for its own assess",
                  "owner": "research agent, reporting to the operator", "done_when": "the transcriber's name and product page are in hand, or it is confirmed the post never names it",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```