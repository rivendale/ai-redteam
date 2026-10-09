**VERDICT:** needs-decision. QuietVoice may help with goal 1, but it costs $9/month after a 14-day free trial, and our constraints need the host's approval for any new paid subscription (and any new account). Its 99% claim has also never been measured on speech.

**WHAT IT IS:** A vendor blog post, "QuietVoice removes 99% of background noise", by QuietVoice, posted 2026-09-24. I read it from a saved snapshot captured 2026-10-09 (`work/snapshot.md`, `work/meta.json`), not live. The post does not say:
- what the plugin format is (VST, AU, etc.);
- whether it runs on Mac or in Reaper;
- whether it processes audio locally or in the cloud;
- whether it needs an account;
- what the license or terms are.

**CLAIMS CHECKED:**
- **"The fan noise dropped by 20 dB on our test":** PROBABLE. It is the vendor's own measurement of one 10-second desk-fan recording, with no method, files or tool described. Not load-bearing.
- **"20 dB = 99% less noise energy":** CONFIRMED as arithmetic, since a 20 dB drop is 10⁻² of the energy. Not load-bearing.
- **"Removes 99% of background noise" in general:** UNVERIFIED, and load-bearing. This joins a fact to an inference. The fact is one fan, one clip. The inference is that it holds for all background noise. The post says *"The recording used for the test is the only one we have measured. It contains no speech."* The study design is n=1, a single noise type, no speech present, and no check of how speech sounds afterward. A noise remover's real test is how much noise it removes while keeping the voice intact, and that was not measured. The post does not show the claim is false, but nothing in it supports the general claim either.
- **"Works on voices too":** UNVERIFIED, and load-bearing. The only evidence is "users tell us". There are no numbers and no samples.
- **The sender's "our editing is slow because of noise cleanup":** UNVERIFIED, and load-bearing. The context file says editing time goes into hand cuts of every silence and filler word in Reaper. It does not mention noise cleanup at all. A noise plugin does not make those cuts. If noise cleanup is only a small part of the 2-hour target, this saves little.

**FIT:**
- **Goal:** Goal 1 (cut editing time to under 2 hours per episode), but only if noise cleanup is a real share of editing time.
- **Overlap:** Nothing in use does automated noise reduction. Reaper is the editor, and ffmpeg is used only by loudness.py. Reaper's built-in tools are not listed as part of the workflow.
- **Burden:** One plugin install on the Mac mini, likely an account for the trial, and remembering to cancel before day 14.
- **Cost:** Free for 14 days, then $9/month (read 2026-10-09 from the snapshot). That is over the $0 quarterly budget unless approved. The terms are not shown.
- **Risks:**
  - Unknown Mac/Reaper compatibility.
  - Unknown whether audio is uploaded to QuietVoice. This would be raw episode audio, not listener data, but it would still go to a new party.
  - A subscription for a core editing step creates lock-in.
  - The license and terms are not read.
  - The source is the vendor's own marketing.

**NEXT ACTION:** The operator asks the host whether to approve a 14-day trial (and any account it needs), with these conditions:
- **Test material:** one real raw episode recording of ours, not a demo clip.
- **Measures:** time the noise-cleanup step with and without QuietVoice, and listen for damage to the voice.
- **Stop:** cancel before day 14 if it saves under ~15 minutes per episode or audibly harms speech.
- **Before asking:** the operator should time how long noise cleanup takes today versus silence and filler cuts, so the host knows what is at stake.
- **Done when:** the host has said yes or no.
- **Hand-off:** none.

**CONFIDENCE:** Medium. The post is resolved (from a same-day snapshot) and a context file is present. However, the claims the verdict rests on (that it works on speech, and that noise cleanup is what makes editing slow) are UNVERIFIED. Mac/Reaper support and where audio is processed are also unknown.

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "money",
  "item": {"type": "post",
           "identity": "QuietVoice blog, 'QuietVoice removes 99% of background noise', by QuietVoice, posted 2026-09-24 (read from snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "fan noise dropped by 20 dB in their test", "evidence": "vendor's own single 10-second desk-fan recording, no method or files given", "status": "PROBABLE", "load_bearing": false},
    {"claim": "20 dB equals 99% less noise energy", "evidence": "arithmetic: -20 dB is 10^-2 of the energy", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "removes 99% of background noise in general", "evidence": "one fan recording only; post says it is the only one measured and it contains no speech", "status": "UNVERIFIED"},
    {"claim": "works on voices too", "evidence": "'users tell us', no measurement or samples", "status": "UNVERIFIED"},
    {"claim": "our editing is slow because of noise cleanup (sender)", "evidence": "context file attributes editing time to hand cuts of silences and filler words and does not mention noise cleanup", "status": "UNVERIFIED"}
  ],
  "fit": {"goal": "goal 1: cut editing time to under 2 hours per episode, only if noise cleanup is a real share of editing time",
          "overlap": "none in use for noise reduction; Reaper edits, ffmpeg only runs loudness.py",
          "burden": "plugin install on the Mac mini, likely a new account, cancel before day 14",
          "risks": ["Mac/Reaper compatibility not stated", "unknown whether audio is processed in the cloud", "license and terms not shown", "subscription lock-in for an editing step", "evidence is vendor marketing, n=1, no speech"],
          "cost": {"price": "free for 14 days, then $9/month", "tier": "single plan as described", "limits": "not stated", "terms": "not shown in the post", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Ask the host to approve or decline a 14-day trial tested on one real raw episode, timing noise cleanup with and without it and listening for voice damage",
                  "owner": "operator",
                  "done_when": "the host has approved or declined the trial",
                  "stop_condition": "cancel before day 14 if it saves under about 15 minutes per episode or audibly harms speech",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```