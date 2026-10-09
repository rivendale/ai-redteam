**VERDICT:** `watch`. One session in this recap touches goal 3: a demo of automatic transcripts corrected by a person. But the post names no tool, price or method, so there is nothing to adopt or trial from it yet.

**WHAT IT IS:** A post, "Podcast conference recap", dated 2026-09-30, at https://posts.example.test/podcast-movement-recap. I read it from a saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not live. No author is given. The post is a list of six one-line session topics with no detail.

**CLAIMS CHECKED:**
- **"A ten-minute demo of automatic transcripts that are corrected by a person before publishing" (day 2): PROBABLE.** The recap reports that the session happened. It does not say which tool was used, what it costs, whether it runs locally or in the cloud, or what output format it produces. *The verdict rests on this.*
- **"12 minutes of correction per 45-minute episode": UNVERIFIED.** This figure comes from a single demo. The post gives no audio conditions (speaker count, crosstalk, accents), no error rate, and no sense of how strict the correction was. Our episodes are 45 minutes, so the number would map directly onto our workflow if it held. Nothing in the post settles whether it does. *The verdict rests on this.*
- **The other sessions** (sponsorship rates, listener surveys, dynamic ad insertion, merch, keynote) make no checkable claims and do not bear on goal 3. Listener surveys could relate to goal 2, but the post gives no content to assess.

**FIT:**
- **Goal:** Goal 3 (a transcript with every episode), via the workflow idea: automatic transcript, then human correction, then publish.
- **Overlap:** Nothing we use produces transcripts today. Reaper, ffmpeg/loudness.py, Buzzsprout, Mailchimp, Google Docs and Hugo do not do this job as listed in our context file.
- **Burden:** If the 12-minute figure held, that would be about 12 minutes of correction per weekly episode, plus a step to publish the transcript (Buzzsprout or the Hugo site). Goal 1 caps editing at 2 hours per episode. This correction time would sit alongside editing and should be counted against that budget.
- **Cost:** Not stated in the post, as read on 2026-10-09.
- **Risks:** The tool is unknown. A hosted transcription service would likely mean a new account and/or payment, and episode audio would go to a new party. Our constraints require the host's approval for those, so any specific tool found later would probably be `needs-decision`. A tool that runs locally on the Macs would avoid the data and account issues but still needs its license checked. GPL/AGPL is fine for a tool we run on our own machines.

**NEXT ACTION:** The operator finds out which tool or vendor the day-2 transcript demo used (conference session listing or speaker slides). If one is named, they send that tool for its own `assess`. **Done when:** a tool is named and sent for assessment, or it is confirmed that the session materials name none. **Hand-off:** none, because the post has nothing beyond the one-line idea to borrow.

**CONFIDENCE:** medium. The context file is present and the post is read from a dated snapshot. The figure the verdict leans on (12 minutes per 45-minute episode) is UNVERIFIED, and the post is too thin to say anything about a specific tool.

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "post", "identity": "\"Podcast conference recap\", posted 2026-09-30, no author given, https://posts.example.test/podcast-movement-recap (read from snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "a day-2 session demoed automatic transcripts corrected by a person before publishing",
     "evidence": "the recap lists the session; no tool, price or method named", "status": "PROBABLE"},
    {"claim": "correction takes 12 minutes per 45-minute episode",
     "evidence": "a single demo figure; no audio conditions, error rate or method given", "status": "UNVERIFIED"},
    {"claim": "other sessions: sponsorship rates, listener surveys, dynamic ad insertion, merch, closing keynote",
     "evidence": "topic names only, no content", "status": "PROBABLE", "load_bearing": false}
  ],
  "fit": {"goal": "goal 3: publish a transcript with every episode (the auto-transcript plus human-correction workflow)",
          "overlap": "none: no tool in use produces transcripts",
          "burden": "about 12 minutes of correction per episode if the figure holds, plus publishing the transcript; counts toward the goal-1 time budget",
          "risks": ["tool unknown", "a hosted service would likely need a new account or payment and send episode audio to a new party (needs host approval)", "license unknown"],
          "cost": {"price": "not stated", "tier": "not stated", "limits": "not stated", "terms": "not stated",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Find which tool or vendor the day-2 transcript demo used (session listing or slides) and send it for its own assess",
                  "owner": "operator",
                  "done_when": "a tool is named and sent for assessment, or it is confirmed the session materials name none",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```