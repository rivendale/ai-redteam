VERDICT: needs-decision. It may serve goal 1, but keeping it is a new paid subscription ($9/month after a 14-day free trial). Our constraints require the host's approval for that, and the trial may also need an account. The "99%" figure comes from one 10-second desk-fan clip with no speech in it, so it says nothing yet about noise cleanup on our episodes.

WHAT IT IS: A vendor blog post, "QuietVoice removes 99% of background noise", by QuietVoice, posted 2026-09-24. I read it from a saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not live. Product terms as read: free for 14 days, then $9/month. The post does not say which plugin formats it supports (AU/VST), whether it runs on macOS or in Reaper, whether processing is local or in the cloud, or whether the trial needs an account or a card.

CLAIMS CHECKED:
- "The desk-fan noise dropped by 20 dB": the evidence is the vendor's own test on one 10-second fan recording, with no method, tool or settings given. **PROBABLE**. Not load-bearing.
- "20 dB is 99% less noise energy": this is arithmetic. 20 dB is a 100× power ratio, which is 99% less energy. **CONFIRMED**. Not load-bearing.
- "QuietVoice removes 99% of background noise" (general, as the title and the sender put it): the only evidence is the fan clip. The post itself says it is "the only one we have measured" and that it "contains no speech". Removing noise from under a voice is the case that matters for a podcast, and it was not tested. **UNVERIFIED**. Load-bearing, because it is why the item might serve goal 1.
- "Users tell us it works on voices too": this is unnamed anecdote with no measurement. **UNVERIFIED**. Load-bearing.
- Sender: "worth trying" because noise cleanup slows our editing: the post gives no data on editing time. Our context file says the hand work is cutting silences and filler words, and it lists no noise-cleanup step. If noise cleanup is a real time sink, that is worth adding to the context file. **UNVERIFIED**. Load-bearing.
- "Free for 14 days, then $9/month": this is the vendor's own terms in the post. **CONFIRMED**. Load-bearing for the needs-decision verdict.

FIT:
- **Goal:** Goal 1 (cut editing to under 2 hours per episode), but only if noise cleanup is a real part of the edit and the tool works on speech. Neither is shown.
- **Overlap:** Nothing in use does noise reduction. Reaper (in use) has built-in noise reduction (ReaFIR in subtract mode). That should be the free baseline to compare against before paying for anything.
- **Burden:** A plugin install on the Mac mini, probably a vendor account and licence, and one more step per episode.
- **Cost:** Free for 14 days, then $9/month, about $108/year (read 2026-10-09 from the snapshot). Our budget is $0 unless approved, and no new paid subscription is allowed without the host's approval.
- **Risks:**
  - Mac and Reaper compatibility is not stated.
  - Install path and signing are unknown.
  - It is unknown whether audio is processed locally or uploaded. Raw episode audio leaving the machine would be a new data flow.
  - It is a subscription, so we would be locked in for as long as we depend on it.
  - The only evidence is the vendor's own marketing.

NEXT ACTION:
- **Action:** The host decides whether to approve a 14-day free trial, with a $9/month subscription to follow only if it proves itself. The test plan for the trial:
  1. Confirm it runs locally as an AU/VST in Reaper on macOS.
  2. Run it on the raw audio of one recent 45-minute episode.
  3. Time noise cleanup and compare it with ReaFIR on the same file.
  4. Listen for artifacts on the voice.
- **Owner:** the host (operator).
- **Done when:** the host has approved or declined. If approved, done when the timed comparison is written down.
- **Stop condition:** cancel before day 14 if any of these hold:
  - it saves less than about 15 minutes per episode compared with ReaFIR;
  - it audibly degrades the voice;
  - it needs a card up front with auto-renewal that cannot be cancelled first;
  - it uploads audio.
- **Hand-off:** none.

CONFIDENCE: medium. A context file is present and the snapshot is readable. Every load-bearing performance claim is UNVERIFIED, because the only test had no speech in it. I also worked from a snapshot, and compatibility, processing location and trial terms are not stated.

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "money",
  "item": {"type": "post", "identity": "QuietVoice blog, 'QuietVoice removes 99% of background noise', posted 2026-09-24 (snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "desk-fan noise dropped by 20 dB", "evidence": "vendor's own test on one 10-second fan recording, no method given", "status": "PROBABLE",
     "load_bearing": false},
    {"claim": "20 dB equals 99% less noise energy", "evidence": "arithmetic: 20 dB is a 100x power ratio", "status": "CONFIRMED",
     "load_bearing": false},
    {"claim": "removes 99% of background noise in general", "evidence": "only one recording measured, and it contains no speech (the post's own words)", "status": "UNVERIFIED"},
    {"claim": "works on voices too", "evidence": "unnamed user anecdote, no measurement", "status": "UNVERIFIED"},
    {"claim": "it would speed up our editing (sender)", "evidence": "no timing data in the post; context file names hand cutting, not noise cleanup, as the manual work", "status": "UNVERIFIED"},
    {"claim": "free for 14 days, then $9/month", "evidence": "vendor's stated terms in the post", "status": "CONFIRMED"}
  ],
  "fit": {"goal": "goal 1: cut editing time to under 2 hours per episode, if noise cleanup is a real part of it",
          "overlap": "no noise-reduction tool listed; Reaper (in use) has built-in ReaFIR noise reduction as a free baseline",
          "burden": "plugin install on the Mac mini, likely a vendor account, one extra step per episode",
          "risks": ["paid subscription needs host approval; budget is $0", "Mac/Reaper plugin compatibility not stated", "unknown whether audio is processed locally or uploaded", "install path and signing unknown", "only evidence is vendor marketing"],
          "cost": {"price": "free 14 days, then $9/month", "tier": "single plan as stated", "limits": "not stated", "terms": "not stated beyond price",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Host decides whether to approve a 14-day free trial; if approved, run it in Reaper on one episode's raw audio and time noise cleanup against ReaFIR on the same file",
                  "owner": "host (operator)", "done_when": "the host has approved or declined, and if approved, the timed comparison is written down",
                  "stop_condition": "cancel before day 14 if it saves under ~15 minutes per episode vs ReaFIR, audibly harms the voice, requires uncancellable auto-renewal, or uploads audio",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```