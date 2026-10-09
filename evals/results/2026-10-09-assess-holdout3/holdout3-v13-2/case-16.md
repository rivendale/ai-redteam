VERDICT: watch. The recap touches goal 3 only in one line: a demo of automatic transcripts corrected by a person. It names no tool, link, price or method, so there is nothing to act on yet. A named tool with its price and terms would change the answer.

WHAT IT IS: Post "Podcast conference recap", posted 2026-09-30, at https://posts.example.test/podcast-movement-recap. The author is not given in the snapshot. I read the saved snapshot captured on 2026-10-09 (work/snapshot.md, work/meta.json), not the live page. It is resolved: the snapshot is readable text. It is a six-item list of conference sessions over three days.

CLAIMS CHECKED:
- *The recap names a tool, vendor or link for the transcript demo.* The full snapshot text describes "a ten-minute demo of automatic transcripts that are corrected by a person before publishing" and names no product, speaker or URL. **REFUTED.** Nothing in the post identifies what was shown. The verdict rests on this.
- *Correcting the transcript takes 12 minutes per 45-minute episode.* The only evidence is a one-line figure from a ten-minute demo. There is no tool, no sample size, no accuracy measure, no audio conditions and no statement of what "corrected" covered. **UNVERIFIED.** Our episodes are also 45 minutes, so the figure would be relevant if it held. The verdict does not rest on it.
- *The rest of the recap (sponsorship rates, listener surveys, dynamic ad insertion, merch, keynote) bears on goal 3.* The snapshot text shows no transcript content in those items. **CONFIRMED** that none of them bear on goal 3. Not load-bearing.

FIT:
- **Goal:** goal 3 (publish a transcript with every episode). It only points at a workflow (machine transcript, then human correction), not at anything we could use.
- **Overlap:** nothing in our context file produces transcripts today. Reaper, ffmpeg/loudness.py, Buzzsprout, Mailchimp, Google Docs and Hugo are not listed as doing this. So there is no overlap, and also nothing named to adopt.
- **Burden:** unknown until a tool is named. The workflow itself implies about 12 minutes of human correction per episode, if the figure holds.
- **Cost:** the post is free to read. No price or tier is given for any tool (checked 2026-10-09).
- **Risks:** none from the post itself. Any transcription service it might lead to could need a new account or subscription and would send episode audio to a new party. Both need the host's approval under our constraints. That would be judged when assessing the actual tool.

NEXT ACTION: The operator finds out which tool or vendor gave the transcript demo on day 2 (from the conference agenda or the session recording) and sends that tool's page to `assess`. Done when a named tool's page is assessed against goal 3, or when the operator records that the demo cannot be identified. Hand-off: none. A single sentence is not worth harvesting.

CONFIDENCE: medium. The item is resolved and the context file is present. The verdict rests on what the snapshot visibly lacks. However, I read only a saved copy, not the live page, and the one useful figure (12 minutes) is unverified.

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "post", "identity": "Podcast conference recap, posted 2026-09-30, https://posts.example.test/podcast-movement-recap (author not given; snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "the recap names a tool, vendor or link for the automatic-transcript demo", "evidence": "snapshot text: the demo is described in one line with no product, speaker or URL", "status": "REFUTED"},
    {"claim": "12 minutes of correction per 45-minute episode", "evidence": "one figure from a ten-minute demo; no tool, sample, accuracy measure or method given", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "the other recap items (sponsorship, surveys, ad insertion, merch, keynote) bear on goal 3", "evidence": "snapshot text: none mention transcripts", "status": "REFUTED",
     "load_bearing": false}
  ],
  "fit": {"goal": "publish a transcript with every episode (goal 3), only as a described workflow", "overlap": "nothing in use produces transcripts",
          "burden": "unknown until a tool is named; the demo implies about 12 minutes of human correction per episode",
          "risks": ["no tool named, so license, terms and data handling cannot be checked", "a transcription service would likely need a new account and would send episode audio to a new party, both needing the host's approval"],
          "cost": {"price": "none named", "tier": "none named", "limits": "unknown", "terms": "unknown",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Identify the tool or vendor behind the day-2 transcript demo (agenda or session recording) and send its page to assess",
                  "owner": "operator", "done_when": "a named tool's page has been assessed against goal 3, or it is recorded that the demo cannot be identified",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```